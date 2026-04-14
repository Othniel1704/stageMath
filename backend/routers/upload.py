from fastapi import APIRouter, File, UploadFile, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from services.ai_parser import analyze_cv_file
from services.profile_service import upsert_profile_antigravity
import logging
import os
import tempfile

router = APIRouter()

class ProfilResponse(BaseModel):
    message: str
    filename: str
    skills: List[str]
    raw_text_preview: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    profile_saved: bool = False
    chemin_acces_local: Optional[str] = None

async def get_user_id_from_token(token: str) -> Optional[str]:
    """Extrait l'user_id depuis le token JWT."""
    try:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
        user_resp = sb.auth.get_user(token)
        return user_resp.user.id if user_resp and user_resp.user else None
    except Exception as e:
        logging.warning(f"Token invalide: {e}")
        return None

@router.post("/upload-cv", response_model=ProfilResponse)
async def upload_cv(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg", ".webp"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté. Utilisez : {', '.join(allowed_extensions)}"
        )

    try:
        content = await file.read()

        # Sauvegarder temporairement le fichier localement pour Antigravity
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(content)
            chemin_acces_local = temp_file.name

        # Analyse IA du CV (one-shot extraction)
        analysis = analyze_cv_file(content, file.filename)

        skills      = analysis.get("skills", [])
        raw_text    = analysis.get("raw_text", "")
        name        = analysis.get("candidate_name", "")
        email       = analysis.get("candidate_email", "")

        # Convertir les compétences en chaîne pour Antigravity
        competences_extraites = ", ".join(skills) if skills else ""

        # Générer l'embedding du CV pour le matching vectoriel
        from services.embedding_service import generate_cv_embedding
        cv_embedding = generate_cv_embedding({
            'raw_cv_text': raw_text,
            'competences_extraites': competences_extraites
        })

        # Sauvegarder le profil si un token Bearer est présent (utilisateur connecté)
        profile_saved = False
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1]
            user_id = await get_user_id_from_token(token)

        if user_id:
            # Utiliser la nouvelle fonction Antigravity pour sauvegarder
            profile_saved = await upsert_profile_antigravity(
                user_id=user_id,
                candidate_name=name,
                candidate_email=email,
                chemin_acces_local=chemin_acces_local,
                competences_extraites=competences_extraites,
                raw_cv_text=raw_text,
                cv_embedding=cv_embedding,
                user_token=token
            )

        return ProfilResponse(
            message="CV analysé avec succès (Antigravity)",
            filename=file.filename,
            skills=skills,
            raw_text_preview=raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
            candidate_name=name,
            candidate_email=email,
            profile_saved=profile_saved,
            chemin_acces_local=chemin_acces_local if profile_saved else None
        )

    except Exception as e:
        logging.error(f"Erreur lors de l'upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du CV: {str(e)}")
