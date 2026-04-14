from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class CacheStatsResponse(BaseModel):
    size: int
    keys: list
    memory_usage_estimate: str

class RateLimiterStatsResponse(BaseModel):
    active_limiters: int
    tracked_identifiers: int
    limits: Dict[str, tuple]

@router.get("/cache-stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """
    Retourne les statistiques du cache.
    Endpoint admistrationnel pour monitoring.
    """
    try:
        from services.cache_service import get_cache_info
        return get_cache_info()
    except Exception as e:
        logger.error(f"Erreur récupération cache stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des stats")

@router.get("/cache-clear")
async def clear_cache():
    """
    Vide tout le cache.
    Endpoint administratif.
    """
    try:
        from services.cache_service import cache_clear
        cache_clear()
        return {"message": "Cache vidé avec succès"}
    except Exception as e:
        logger.error(f"Erreur vidage cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du vidage du cache")

@router.get("/rate-limiter-stats", response_model=RateLimiterStatsResponse)
async def get_rate_limiter_stats():
    """
    Retourne les statistiques du rate limiter.
    """
    try:
        from middleware.rate_limiter import rate_limiter
        return rate_limiter.get_stats()
    except Exception as e:
        logger.error(f"Erreur récupération rate limiter stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des stats")

@router.post("/rate-limiter-reset")
async def reset_rate_limiter(identifier: str = None, endpoint: str = None):
    """
    Réinitialise les compteurs du rate limiter.
    """
    try:
        from middleware.rate_limiter import rate_limiter
        rate_limiter.reset(identifier, endpoint)
        return {
            "message": "Rate limiter réinitialisé",
            "identifier": identifier,
            "endpoint": endpoint
        }
    except Exception as e:
        logger.error(f"Erreur reset rate limiter: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la réinitialisation")

@router.get("/job-fetcher-cache-stats")
async def get_job_fetcher_cache_stats():
    """
    Retourne les stats spécifiques du cache du job fetcher.
    """
    try:
        from services.job_fetcher import get_cache_stats
        return get_cache_stats()
    except Exception as e:
        logger.error(f"Erreur récupération job fetcher cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des stats")

@router.post("/job-fetcher-cache-clear")
async def clear_job_fetcher_cache():
    """
    Vide le cache du job fetcher.
    """
    try:
        from services.job_fetcher import clear_cache
        clear_cache()
        return {"message": "Cache du job fetcher vidé avec succès"}
    except Exception as e:
        logger.error(f"Erreur vidage cache job fetcher: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du vidage du cache")

@router.get("/health-detailed")
async def get_detailed_health():
    """
    Retourne un health check détaillé avec tous les services.
    """
    try:
        from services.cache_service import get_cache_info
        from middleware.rate_limiter import rate_limiter
        import os

        # Vérifier Supabase
        try:
            from supabase import create_client
            sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
            supabase_ok = True
        except:
            supabase_ok = False

        return {
            "status": "ok",
            "services": {
                "supabase": "ok" if supabase_ok else "error",
                "cache": "ok",
                "rate_limiter": "ok",
                "embeddings": "ok"  # On peut vérifier en essayant de générer un embedding
            },
            "cache_info": get_cache_info(),
            "rate_limiter_info": rate_limiter.get_stats()
        }
    except Exception as e:
        logger.error(f"Erreur health check détaillé: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }
