from datetime import datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# Cache simple en mémoire
_cache = {}
_cache_ttl = {}

def cache_get(key: str, ttl_minutes: int = 30) -> Optional[Any]:
    """
    Récupère une valeur du cache si elle n'est pas expirée.
    """
    if key not in _cache:
        return None

    # Vérifier la TTL
    if key in _cache_ttl:
        timestamp = _cache_ttl[key]
        if datetime.now() - timestamp > timedelta(minutes=ttl_minutes):
            # Cache expiré, le supprimer
            del _cache[key]
            del _cache_ttl[key]
            logger.debug(f"Cache expiré pour la clé: {key}")
            return None

    logger.debug(f"Cache hit pour la clé: {key}")
    return _cache[key]

def cache_set(key: str, value: Any) -> None:
    """
    Stocke une valeur dans le cache avec timestamp.
    """
    _cache[key] = value
    _cache_ttl[key] = datetime.now()
    logger.debug(f"Cache set pour la clé: {key}")

def cache_delete(key: str) -> None:
    """
    Supprime une clé du cache.
    """
    if key in _cache:
        del _cache[key]
    if key in _cache_ttl:
        del _cache_ttl[key]
    logger.debug(f"Cache supprimé pour la clé: {key}")

def cache_clear() -> None:
    """
    Vide tout le cache.
    """
    global _cache, _cache_ttl
    _cache.clear()
    _cache_ttl.clear()
    logger.info("Cache entièrement vidé")

def get_cache_size() -> int:
    """
    Retourne le nombre d'éléments dans le cache.
    """
    return len(_cache)

def get_cache_info() -> dict:
    """
    Retourne des infos sur l'état du cache.
    """
    return {
        "size": len(_cache),
        "keys": list(_cache.keys()),
        "memory_usage_estimate": f"{len(str(_cache)) / 1024:.2f} KB"
    }
