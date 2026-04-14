from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from services.matching import find_matching_jobs, extract_location_from_cv, detect_missing_info, has_meaningful_embedding
from middleware.auth import get_current_user, get_authenticated_client
from supabase import Client
from middleware.rate_limiter import check_rate_limit
import logging

router = APIRouter()

class MatchRequest(BaseModel):
    location: Optional[str] = None
    preferred_contract: Optional[str] = None
    page: int = 1
    page_size: int = 20

class MissingInfoResponse(BaseModel):
    missing_fields: List[str]
    detected_location: Optional[str]

class JobMatchResponse(BaseModel):
    id: str
    title: str
    company_name: str
    location: str
    url: str
    contract_type: str
    match_score: int
    skills_required: List[str]
    source: str
    score_color: str
    score_label: Optional[str] = None
    summary: Optional[str] = None
    matching_reasons: List[str] = []
    score_breakdown: dict = {}
    matched_skills: List[str] = []

@router.post("/match/check-info", response_model=MissingInfoResponse)
async def check_missing_info(
    request: Request,
    match_request: MatchRequest,
    sb: Client = Depends(get_authenticated_client)
):
    """
    Analyse les infos du profil utilisateur et signale les champs manquants.
    """
    # Vérifier le rate limit
    await check_rate_limit(request, "/match/check-info")
    
    try:
        user_id = sb.user_id
        profile = sb.table("profiles").select("raw_cv_text, location, preferred_contract").eq("user_id", user_id).execute()

        if not profile.data:
            return MissingInfoResponse(missing_fields=["location", "preferred_contract"], detected_location=None)

        profile_data = profile.data[0]
        raw_text = profile_data.get("raw_cv_text", "")
        detected_location = extract_location_from_cv(raw_text)
        missing = detect_missing_info(raw_text, detected_location)

        return MissingInfoResponse(
            missing_fields=missing,
            detected_location=detected_location
        )

    except Exception as e:
        logging.error(f"Erreur check-info: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse du profil")


class MatchResponse(BaseModel):
    jobs: List[JobMatchResponse]
    total_count: int
    page: int
    page_size: int
    has_more: bool
    mobility_added_by_default: bool = False
    location_used: str

@router.post("/match", response_model=MatchResponse)
async def match_jobs(
    request: Request,
    match_request: MatchRequest,
    sb: Client = Depends(get_authenticated_client)
):
    """
    Matching moderne basé sur les embeddings vectoriels.
    """
    # Vérifier le rate limit
    await check_rate_limit(request, "/match")
    
    try:
        user_id = sb.user_id
        profile = sb.table("profiles").select("competences_extraites, cv_embedding").eq("user_id", user_id).execute()

        if not profile.data:
            raise HTTPException(status_code=404, detail="Profil non trouvé - Veuillez uploader un CV d'abord")

        profile_data = profile.data[0]

        # Vérifier qu'il y a soit des compétences extraites soit un embedding
        has_competences = profile_data.get("competences_extraites", "").strip()
        has_embedding = has_meaningful_embedding(profile_data.get("cv_embedding"))

        if not has_competences and not has_embedding:
            raise HTTPException(status_code=400, detail="Aucune compétence extraite - Veuillez re-uploader votre CV")

        # Utiliser le nouveau système de matching avec le token courant pour respecter le RLS
        token = sb.postgrest.headers.get("Authorization", "").replace("Bearer ", "")
        result = await find_matching_jobs(
            user_id=user_id,
            user_location=match_request.location,
            preferred_contract=match_request.preferred_contract,
            user_token=token,
            limit=match_request.page_size
        )

        return MatchResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur matching: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du matching")
