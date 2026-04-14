import time
import logging
import requests
from functools import wraps
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)

def retry_on_failure(
    max_retries: int = 3,
    initial_delay: float = 1,
    max_delay: float = 60,
    exponential_base: float = 2,
    exceptions: tuple = (requests.RequestException, IOError, TimeoutError)
):
    """
    Décorateur pour retry automatique avec backoff exponentiel.
    
    Args:
        max_retries: Nombre maximum de tentatives
        initial_delay: Délai initial en secondes
        max_delay: Délai maximum en secondes
        exponential_base: Base de croissance pour le backoff exponentiel
        exceptions: Tuple des exceptions à retry
    
    Example:
        @retry_on_failure(max_retries=3, initial_delay=1)
        def fetch_jobs():
            return requests.get(url).json()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    logger.debug(f"Tentative {attempt + 1}/{max_retries} pour {func.__name__}")
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        # Dernière tentative
                        logger.error(
                            f"❌ {func.__name__} échoué après {max_retries} tentatives: {str(e)}"
                        )
                        raise

                    # Calculer le délai avec backoff exponentiel
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    logger.warning(
                        f"⚠️ Tentative {attempt + 1}/{max_retries} échouée. "
                        f"Réessai dans {delay:.1f}s: {str(e)}"
                    )
                    time.sleep(delay)

                except Exception as e:
                    # Exception non préévue
                    logger.error(f"Erreur non attendue dans {func.__name__}: {str(e)}")
                    raise

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_with_tenacity(
    max_attempts: int = 3,
    wait_multiplier: float = 1,
    exceptions: tuple = (requests.RequestException, IOError, TimeoutError)
):
    """
    Décorateur Tenacity pour retry plus avancé (alternative).
    Utilise la librairie tenacity qui offre plus de contrôle.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=wait_multiplier, min=1, max=60),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


class RetryManager:
    """
    Classe pour gérer les retries de manière plus sophistiquée.
    Peut tracker les tentatives et les erreurs.
    """

    def __init__(self, max_retries: int = 3, initial_delay: float = 1):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.attempt_count = 0
        self.last_error = None

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute une fonction avec retry automatique.
        """
        self.attempt_count = 0
        self.last_error = None

        for attempt in range(self.max_retries):
            self.attempt_count = attempt + 1
            try:
                logger.debug(f"Tentative {self.attempt_count}/{self.max_retries}")
                return func(*args, **kwargs)

            except Exception as e:
                self.last_error = e

                if self.attempt_count == self.max_retries:
                    logger.error(
                        f"Échec après {self.max_retries} tentatives: {str(e)}"
                    )
                    raise

                delay = self.initial_delay * (2 ** (attempt))
                logger.warning(
                    f"Tentative {self.attempt_count} échouée. "
                    f"Réessai dans {delay:.1f}s: {str(e)}"
                )
                time.sleep(delay)

    def get_stats(self) -> dict:
        """
        Retourne les stats du dernier execution.
        """
        return {
            "attempts": self.attempt_count,
            "last_error": str(self.last_error),
            "success": self.last_error is None
        }
