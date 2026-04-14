from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from middleware.auth import get_authenticated_client
from supabase import Client
import logging

router = APIRouter()

class JobListResponse(BaseModel):
    jobs: List[dict]
    total_count: int
    page: int
    page_size: int
    has_more: bool

@router.get("/jobs", response_model=JobListResponse)
async def get_all_jobs(
    page: int = 1,
    page_size: int = 20,
    sb: Client = Depends(get_authenticated_client)
):
    """
    Récupère toutes les offres d'emploi, triées par date de création.
    """
    try:
        # Calculer l'offset pour la pagination
        start = (page - 1) * page_size
        end = start + page_size - 1

        # Récupérer les offres
        result = sb.table("job_offers") \
            .select("*", count="exact") \
            .order("created_at", desc=True) \
            .range(start, end) \
            .execute()

        jobs = result.data or []
        total_count = result.count if result.count is not None else len(jobs)

        # Nettoyer les données pour le frontend (renommer ou ajouter des champs attendus)
        formatted_jobs = []
        for job in jobs:
            description = job.get("description", "") or ""
            summary = " ".join(description.split())
            if len(summary) > 220:
                summary = f"{summary[:219].rsplit(' ', 1)[0]}…"
            elif not summary:
                summary = "Description non disponible."

            formatted_jobs.append({
                "id": job["id"],
                "title": job["title"],
                "company_name": job.get("company_name", "Entreprise confidentielle"),
                "location": job.get("location", "Distant"),
                "url": job["url"],
                "contract_type": job.get("contract_type", "Non précisé"),
                "match_score": 0,  # Pas de score IA dans le catalogue complet
                "skills_required": job.get("skills_required", []),
                "source": job.get("source", "StageMatch"),
                "score_color": "neutral",
                "score_label": "catalog",
                "summary": summary,
                "matching_reasons": [],
                "score_breakdown": {
                    "semantic": 0,
                    "skills": 0,
                    "location": 0,
                    "contract": 0
                },
                "matched_skills": []
            })

        return JobListResponse(
            jobs=formatted_jobs,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=total_count > end + 1
        )

    except Exception as e:
        logging.error(f"Erreur récupération catalogue: {e}")
        raise HTTPException(status_code=500, detail="Impossible de récupérer les offres.")
