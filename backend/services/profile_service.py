import os
import logging
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")


def _get_client(user_token: Optional[str] = None) -> Optional[Client]:
    """
    Crée un client Supabase. Si un token utilisateur est fourni,
    on l'injecte dans les headers pour respecter le RLS.
    Sinon on utilise la clé anon classique.
    """
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        if user_token:
            # Injecter le JWT de l'utilisateur pour que RLS
            # reconnaisse auth.uid() correctement
            client.postgrest.auth(user_token)
        return client
    except Exception as e:
        logging.error(f"Supabase client init failed: {e}")
        return None


def sanitize_text(text: Optional[str]) -> str:
    """Supprime les caractères nuls (\0) incompatibles avec Postgres."""
    if text is None:
        return ""
    return text.replace("\u0000", "").replace("\x00", "")


async def upsert_profile_antigravity(
    user_id: str,
    candidate_name: str = "",
    candidate_email: str = "",
    chemin_acces_local: str = "",
    competences_extraites: str = "",
    raw_cv_text: str = "",
    location: Optional[str] = None,
    preferred_contract: Optional[str] = None,
    cv_embedding: Optional[List[float]] = None,
    user_token: Optional[str] = None,
) -> bool:
    """
    Fonction principale de sauvegarde de profil.
    Gère la synchronisation des champs et la persistance dans Supabase.
    """
    client = _get_client(user_token)
    if not client:
        logging.error(f"Impossible d'initialiser le client Supabase pour l'utilisateur {user_id}")
        return False

    try:
        # Nettoyage des caractères nuls (\0) qui font planter Postgres
        candidate_name = sanitize_text(candidate_name)
        candidate_email = sanitize_text(candidate_email)
        competences_extraites = sanitize_text(competences_extraites)
        raw_cv_text = sanitize_text(raw_cv_text)
        location = sanitize_text(location) if location else None
        preferred_contract = sanitize_text(preferred_contract) if preferred_contract else None

        # Nettoyage et préparation des compétences
        skills_list = [s.strip() for s in competences_extraites.split(",") if s.strip()]
        
        data: dict = {
            "user_id": user_id,
            "candidate_name": candidate_name,
            "email": candidate_email,
            "chemin_acces_local": chemin_acces_local,
            "competences_extraites": ", ".join(skills_list),
            "extracted_skills": skills_list,
            "raw_cv_text": raw_cv_text[:5000] if raw_cv_text else "",
            "updated_at": "now()"
        }

        if location:
            data["location"] = location
        if preferred_contract:
            data["preferred_contract"] = preferred_contract
        if cv_embedding is not None:
            data["cv_embedding"] = cv_embedding

        logging.info(f"Tentative d'upsert profil pour {user_id}...")
        
        # Exécution de l'upsert
        # On utilise select() après upsert pour vérifier que la donnée est bien retournée (preuve d'écriture)
        # SUPABASE TIP: .execute() returns a response with 'data'
        result = client.table("profiles").upsert(data, on_conflict="user_id").execute()

        if hasattr(result, 'data') and len(result.data) > 0:
            logging.info(f"✅ Profil sauvegardé avec succès pour {user_id}")
            return True
        else:
            # Fallback diag: Si upsert ne renvoie rien à cause de RLS, on tente un select manuel
            check = client.table("profiles").select("id").eq("user_id", user_id).execute()
            if check.data:
                logging.info(f"✅ Profil déjà présent ou sauvegardé (confirmé par select) pour {user_id}")
                return True
            
            logging.warning(f"⚠️ L'upsert a été tenté mais aucune donnée n'est visible pour {user_id}. Vérifiez les politiques RLS.")
            return False 

    except Exception as e:
        logging.error(f"\u274c Erreur critique lors de la sauvegarde du profil {user_id}: {str(e)}")
        return False


async def upsert_profile(
    user_id: str,
    candidate_name: str = "",
    location: Optional[str] = None,
    preferred_contract: Optional[str] = None,
    skills: List[str] = None,
    raw_text: str = "",
    candidate_email: str = "",
    user_token: Optional[str] = None,
) -> bool:
    """Fallback / Wrapper pour la fonction Antigravity avec régénération d'embedding."""
    
    # 1. Régénérer l'embedding pour que le matching prenne en compte les nouvelles compétences
    from services.embedding_service import generate_cv_embedding
    competences_str = ", ".join(skills) if skills else ""
    
    cv_embedding = generate_cv_embedding({
        'raw_cv_text': raw_text,
        'competences_extraites': competences_str
    })

    return await upsert_profile_antigravity(
        user_id=user_id,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        location=location,
        preferred_contract=preferred_contract,
        competences_extraites=competences_str,
        raw_cv_text=raw_text,
        cv_embedding=cv_embedding,
        user_token=user_token
    )


async def get_profile(user_id: str, user_token: Optional[str] = None) -> Optional[dict]:
    """Récupère le profil d'un utilisateur depuis Supabase."""
    client = _get_client(user_token)
    if not client:
        return None
    try:
        res = client.table("profiles").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logging.error(f"Erreur récupération profil {user_id}: {e}")
        return None
