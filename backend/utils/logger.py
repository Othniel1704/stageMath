import logging
import sys
from datetime import datetime

def setup_logger(name: str = "jobboard_api"):
    """Configure un logger structuré"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Éviter les logs dupliqués
    if logger.handlers:
        return logger

    # Format avec timestamp, niveau, message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Handler fichier (logs persistants)
    try:
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)  # Seulement les warnings et erreurs dans le fichier
        logger.addHandler(file_handler)
    except Exception as e:
        # Si on ne peut pas créer le fichier de log, continuer sans
        console_handler.emit(logging.LogRecord(
            name, logging.WARNING, "", 0,
            f"Impossible de créer le fichier de logs: {e}", (), None
        ))

    return logger

# Logger global
logger = setup_logger()