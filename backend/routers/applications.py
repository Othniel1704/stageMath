from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
import os, logging
from supabase import Client
from dotenv import load_dotenv
from datetime import datetime
from services.profile_service import upsert_profile, get_profile
from middleware.auth import get_authenticated_client

load_dotenv()
router = APIRouter()

STATUS_SAVED_VALUES = ["saved", "Enregistré", "Enregistre"]
STATUS_APPLIED_VALUES = ["applied", "Postulé", "Postule"]


def canonical_status(value: Optional[str]) -> str:
    if value in STATUS_APPLIED_VALUES:
        return "applied"
    return "saved"


def db_status_for(status: str) -> str:
    if status == "applied":
        return "Postulé"
    return "Enregistré"


class ApplicationResponse(BaseModel):
    message: str
    status: str

class SavedJobStateResponse(BaseModel):
    saved_job_ids: List[str]
    applied_job_ids: List[str]
    items: List[dict]

class ApplyConfirmationRequest(BaseModel):
    has_applied: bool  # True si l'utilisateur a postulé, False sinon

@router.post("/save/{job_id}", response_model=ApplicationResponse)
async def save_job_application(job_id: str, sb: Client = Depends(get_authenticated_client)):
    user_id = sb.user_id
    # Vérifier l'offre
    existing = sb.from_("job_offers").select("id").eq("id", job_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Offre introuvable")

    try:
        # Sauvegarder l'offre (statut "saved")
        data = {
            "user_id": user_id,
            "job_offer_id": job_id,
            "status": db_status_for("saved")
        }

        sb.table("saved_jobs").upsert(data, on_conflict="user_id,job_offer_id").execute()

        return ApplicationResponse(
            message="Offre sauvegardée avec succès",
            status="saved"
        )

    except Exception as e:
        logging.error(f"Erreur sauvegarde: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")

@router.put("/apply/{job_id}", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: str,
    request: ApplyConfirmationRequest,
    sb: Client = Depends(get_authenticated_client)
):
    """
    Antigravity: Confirme si l'utilisateur a postulé à l'offre.
    Si oui, change le statut à "Postulé" et l'offre disparaît du Catalogue.
    """
    user_id = sb.user_id
    # Vérifier que l'offre existe dans saved_jobs
    saved_job = sb.table("saved_jobs").select("id").eq("user_id", user_id).eq("job_offer_id", job_id).execute()
    if not saved_job.data:
        raise HTTPException(status_code=404, detail="Offre non sauvegardée")

    try:
        new_status = "applied" if request.has_applied else "saved"
        db_status = db_status_for(new_status)

        # Mettre à jour le statut
        sb.table("saved_jobs").update({
            "status": db_status,
            "updated_at": "now()"
        }).eq("user_id", user_id).eq("job_offer_id", job_id).execute()

        message = "Statut mis à jour : Postulé" if request.has_applied else "Statut mis à jour : Enregistré"

        return ApplicationResponse(
            message=message,
            status=new_status
        )

    except Exception as e:
        logging.error(f"Erreur application: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

@router.get("/saved", response_model=List[dict])
async def get_saved_jobs(sb: Client = Depends(get_authenticated_client)):
    """
    Antigravity: Récupère les offres sauvegardées (Catalogue).
    """
    user_id = sb.user_id
    try:
        # Récupérer les offres sauvegardées avec les détails des jobs
        result = sb.table("saved_jobs").select("""
            id,
            status,
            created_at,
            job_offers (
                id,
                title,
                company_name,
                location,
                url,
                contract_type,
                description,
                source
            )
        """).eq("user_id", user_id).in_("status", STATUS_SAVED_VALUES).execute()

        items = result.data or []
        for item in items:
            item["status"] = canonical_status(item.get("status"))
        return items

    except Exception as e:
        logging.error(f"Erreur récupération saved jobs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération")

@router.get("/applied", response_model=List[dict])
async def get_applied_jobs(sb: Client = Depends(get_authenticated_client)):
    """
    Antigravity: Récupère les offres postulées (Suivi).
    """
    user_id = sb.user_id
    try:
        # Récupérer les offres postulées avec les détails des jobs
        result = sb.table("saved_jobs").select("""
            id,
            status,
            created_at,
            job_offers (
                id,
                title,
                company_name,
                location,
                url,
                contract_type,
                description,
                source
            )
        """).eq("user_id", user_id).in_("status", STATUS_APPLIED_VALUES).execute()

        items = result.data or []
        for item in items:
            item["status"] = canonical_status(item.get("status"))
        return items

    except Exception as e:
        logging.error(f"Erreur récupération applied jobs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération")


@router.get("/dashboard")
async def get_dashboard(sb: Client = Depends(get_authenticated_client)):
    user_id = sb.user_id
    try:
        res = sb.from_("saved_jobs").select("*, job_offers(*)").eq("user_id", user_id).execute()
        items = res.data or []
        
        for item in items:
            item["status"] = canonical_status(item.get("status"))

        saved_count = sum(1 for i in items if i.get("status") == "saved")
        applied_count = sum(1 for i in items if i.get("status") == "applied")
        
        return {
            "stats": {
                "saved": saved_count,
                "applied": applied_count,
                "total": len(items)
            },
            "applications": items
        }
    except Exception as e:
        logging.error(f"Erreur dashboard: {e}")
        raise HTTPException(status_code=500, detail="Impossible de récupérer le suivi")

@router.get("/status-map", response_model=SavedJobStateResponse)
async def get_saved_jobs_status_map(sb: Client = Depends(get_authenticated_client)):
    """
    Retourne l'état de suivi des offres pour l'utilisateur courant.
    Utile pour marquer immédiatement les offres déjà enregistrées ou postulées.
    """
    user_id = sb.user_id
    try:
        result = (
            sb.table("saved_jobs")
            .select("job_offer_id, status, created_at, updated_at")
            .eq("user_id", user_id)
            .execute()
        )

        items = result.data or []
        for item in items:
            item["status"] = canonical_status(item.get("status"))

        saved_job_ids = [item["job_offer_id"] for item in items if item.get("status") == "saved"]
        applied_job_ids = [item["job_offer_id"] for item in items if item.get("status") == "applied"]

        return SavedJobStateResponse(
            saved_job_ids=saved_job_ids,
            applied_job_ids=applied_job_ids,
            items=items,
        )
    except Exception as e:
        logging.error(f"Erreur récupération status-map: {e}")
        raise HTTPException(status_code=500, detail="Impossible de récupérer l'état du suivi")

@router.delete("/{job_id}", response_model=ApplicationResponse)
async def delete_job_application(job_id: str, sb: Client = Depends(get_authenticated_client)):
    """
    Supprime une offre de la liste de suivi (sauvegardée ou postulée).
    """
    user_id = sb.user_id
    try:
        # Supprimer l'entrée
        res = sb.table("saved_jobs").delete().eq("user_id", user_id).eq("job_offer_id", job_id).execute()
        
        return ApplicationResponse(
            message="Offre supprimée avec succès",
            status="deleted"
        )

    except Exception as e:
        logging.error(f"Erreur suppression application: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
