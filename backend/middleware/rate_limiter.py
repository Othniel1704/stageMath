from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Système de rate limiting simple basé sur le temps.
    Limite les requêtes par IP ou user.
    """

    def __init__(self):
        # Structure: {key: [(timestamp, count)]}
        self.requests: Dict[str, list] = {}
        self.limits: Dict[str, Tuple[int, int]] = {}  # {endpoint: (requests, seconds)}

    def set_limit(self, endpoint: str, requests_limit: int, time_window_seconds: int):
        """
        Configure la limite pour un endpoint.
        
        Args:
            endpoint: Chemin de l'endpoint (ex: "/match")
            requests_limit: Nombre maximal de requêtes
            time_window_seconds: Fenêtre de temps en secondes
            
        Example:
            limiter.set_limit("/match", 10, 60)  # 10 requêtes par minute
        """
        self.limits[endpoint] = (requests_limit, time_window_seconds)
        logger.info(f"Rate limit défini: {endpoint} - {requests_limit}/{time_window_seconds}s")

    def is_allowed(self, identifier: str, endpoint: str) -> Tuple[bool, Dict]:
        """
        Vérifie si une requête est autorisée.
        
        Args:
            identifier: IP ou user_id
            endpoint: Chemin de l'endpoint
            
        Returns:
            (allowed, info_dict)
        """
        if endpoint not in self.limits:
            return True, {}

        requests_limit, time_window = self.limits[endpoint]
        now = datetime.now()
        key = f"{identifier}:{endpoint}"

        # Nettoyer les anciennes requêtes
        if key in self.requests:
            cutoff_time = now - timedelta(seconds=time_window)
            self.requests[key] = [
                (timestamp, count) for timestamp, count in self.requests[key]
                if timestamp > cutoff_time
            ]

        # Compter les requêtes actuelles
        if key not in self.requests:
            self.requests[key] = []

        current_count = sum(count for _, count in self.requests[key])

        if current_count >= requests_limit:
            oldest_request = self.requests[key][0][0]
            reset_time = oldest_request + timedelta(seconds=time_window)
            seconds_until_reset = max(0, (reset_time - now).total_seconds())

            return False, {
                "limit": requests_limit,
                "current": current_count,
                "reset_in_seconds": int(seconds_until_reset)
            }

        # Ajouter la nouvelle requête
        self.requests[key].append((now, 1))
        remaining = requests_limit - current_count - 1

        return True, {
            "limit": requests_limit,
            "current": current_count + 1,
            "remaining": remaining
        }

    def reset(self, identifier: str = None, endpoint: str = None):
        """
        Réinitialise les compteurs.
        """
        if identifier and endpoint:
            key = f"{identifier}:{endpoint}"
            if key in self.requests:
                del self.requests[key]
        else:
            self.requests.clear()

    def get_stats(self) -> Dict:
        """
        Retourne les stats du rate limiter.
        """
        return {
            "active_limiters": len(self.limits),
            "tracked_identifiers": len(self.requests),
            "limits": self.limits
        }


# Instance globale
rate_limiter = RateLimiter()

# Limites par défaut
DEFAULT_LIMITS = {
    "/match": (10, 60),           # 10 requêtes par minute
    "/match/check-info": (20, 60), # 20 requêtes par minute
    "/upload-cv": (5, 3600),       # 5 uploads par heure
    "/applications": (20, 60),     # 20 requêtes par minute
}

# Initialiser les limites par défaut
for endpoint, (limit, window) in DEFAULT_LIMITS.items():
    rate_limiter.set_limit(endpoint, limit, window)


async def check_rate_limit(request: Request, endpoint: str = None) -> Dict:
    """
    Midleware pour vérifier le rate limit.
    Utilise l'IP comme identifiant.
    """
    identifier = request.client.host if request.client else "unknown"
    check_endpoint = endpoint or request.url.path

    is_allowed, info = rate_limiter.is_allowed(identifier, check_endpoint)

    if not is_allowed:
        logger.warning(f"Rate limit excédé pour {identifier} sur {check_endpoint}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Trop de requêtes. Réessayez dans {info['reset_in_seconds']} secondes.",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(info["reset_in_seconds"])
            }
        )

    return info
