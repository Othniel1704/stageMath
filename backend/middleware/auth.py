from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging
from supabase import create_client

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware d'authentification centralisé.
    Retourne l'user_id si le token est valide.
    """
    token = credentials.credentials

    try:
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
        user_resp = sb.auth.get_user(token)

        if not user_resp or not user_resp.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré"
            )

        return user_resp.user.id
    except Exception as e:
        logging.error(f"Erreur authentification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur d'authentification"
        )

async def get_authenticated_client(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Client:
    """
    Dépendance FastAPI qui retourne un client Supabase authentifié.
    Injecte automatiquement le token JWT pour respecter RLS.
    """
    token = credentials.credentials
    try:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_ANON_KEY"]
        sb = create_client(url, key)
        
        # Vérifier le token
        user_resp = sb.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré"
            )
            
        # Authentifier le client postgrest pour RLS
        sb.postgrest.auth(token)
        
        # Attacher l'user_id au client pour un accès facile si besoin
        sb.user_id = user_resp.user.id
        
        return sb
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur init client authentifié: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur d'authentification"
        )


async def get_current_user_optional(request: Request) -> Optional[str]:
    """
    Version optionnelle qui ne lève pas d'exception si pas de token.
    Utile pour les endpoints qui peuvent être utilisés avec ou sans auth.
    """
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]

    try:
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
        user_resp = sb.auth.get_user(token)

        if user_resp and user_resp.user:
            return user_resp.user.id
    except Exception as e:
        logging.warning(f"Token optionnel invalide: {e}")

    return None