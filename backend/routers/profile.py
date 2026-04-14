from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from services.profile_service import upsert_profile, get_profile
from middleware.auth import get_authenticated_client
from supabase import Client
import os, logging
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    candidate_name: Optional[str] = None
    location: Optional[str] = None
    preferred_contract: Optional[str] = None
    extracted_skills: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    user_id: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    preferred_contract: Optional[str] = None
    extracted_skills: List[str] = []
    chemin_acces_local: Optional[str] = None
    competences_extraites: Optional[str] = None


@router.get("/profile/me", response_model=ProfileResponse)
async def get_my_profile(sb: Client = Depends(get_authenticated_client)):
    user_id = sb.user_id
    try:
        profile = sb.table("profiles").select("*").eq("user_id", user_id).execute()

        if not profile.data:
            raise HTTPException(status_code=404, detail="Profil non trouvé")

        data = profile.data[0]

        return ProfileResponse(
            user_id=user_id,
            candidate_name=data.get("candidate_name"),
            email=data.get("email"),
            location=data.get("location"),
            preferred_contract=data.get("preferred_contract"),
            extracted_skills=data.get("extracted_skills", []),
            chemin_acces_local=data.get("chemin_acces_local"),
            competences_extraites=data.get("competences_extraites")
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur récupération profil: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du profil")


@router.get("/profile/cv")
async def open_cv_file(sb: Client = Depends(get_authenticated_client)):
    """
    Antigravity: Ouvre le fichier CV local en utilisant le chemin_acces_local.
    """
    user_id = sb.user_id
    try:
        profile = sb.table("profiles").select("chemin_acces_local").eq("user_id", user_id).execute()

        if not profile.data:
            raise HTTPException(status_code=404, detail="Profil non trouvé")

        chemin_acces_local = profile.data[0].get("chemin_acces_local")

        if not chemin_acces_local or not os.path.exists(chemin_acces_local):
            raise HTTPException(status_code=404, detail="Fichier CV non trouvé localement")

        # Retourner le fichier pour téléchargement/visualisation
        return FileResponse(
            path=chemin_acces_local,
            filename=f"CV_{user_id}.pdf",
            media_type="application/pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur ouverture CV: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'ouverture du CV")


@router.put("/profile/me")
async def update_my_profile(
    body: ProfileUpdateRequest,
    sb: Client = Depends(get_authenticated_client),
):
    user_id = sb.user_id
    
    logging.info(f"PUT /profile/me user={user_id} data={body.dict()}")

    # Note: On utilise toujours upsert_profile mais on pourrait passer le client sb directement plus tard
    # Pour l'instant on garde la compatibilité avec le token si besoin
    token = sb.postgrest.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Récupérer l'ancien profil pour préserver le texte brut du CV (nécessaire pour l'embedding)
    current_profile = await get_profile(user_id, token)
    raw_text = current_profile.get("raw_cv_text", "") if current_profile else ""

    saved = await upsert_profile(
        user_id=user_id,
        candidate_name=body.candidate_name or "",
        location=body.location,
        preferred_contract=body.preferred_contract,
        skills=body.extracted_skills or [],
        raw_text=raw_text,
        user_token=token,
    )
    if not saved:
        raise HTTPException(status_code=500, detail="Erreur sauvegarde profil.")
    return {"message": "Profil mis à jour avec succès"}


@router.get("/profile/stats")
async def get_profile_stats(sb: Client = Depends(get_authenticated_client)):
    """
    Retourne des statistiques rapides (nombre de matchs, état du profil).
    """
    user_id = sb.user_id
    try:
        # 1. Vérifier si le profil existe
        profile = sb.table("profiles").select("id, extracted_skills").eq("user_id", user_id).execute()
        has_profile = len(profile.data) > 0
        skills_count = len(profile.data[0].get("extracted_skills", [])) if has_profile else 0

        # 2. Compter les matchs (approximatif pour le dashboard)
        match_count = 0
        if has_profile:
            matches = sb.table("job_offers").select("id", count="exact").execute()
            match_count = matches.count if matches.count is not None else 0

        # 3. Compter les candidatures
        apps = sb.table("saved_jobs").select("id", count="exact").eq("user_id", user_id).execute()
        app_count = apps.count if apps.count is not None else 0

        return {
            "has_profile": has_profile,
            "skills_count": skills_count,
            "match_count": match_count,
            "application_count": app_count,
            "profile_completion": 100 if has_profile and skills_count > 0 else 50 if has_profile else 0
        }
    except Exception as e:
        logging.error(f"Erreur stats profil: {e}")
        return {
            "has_profile": False,
            "skills_count": 0,
            "match_count": 0,
            "application_count": 0,
            "profile_completion": 0
        }
