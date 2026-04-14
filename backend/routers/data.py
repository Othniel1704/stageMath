from fastapi import APIRouter, HTTPException
from services.job_fetcher import fetch_remotive_jobs, fetch_ft_jobs, fetch_jsearch_jobs
from services.cleanup_jobs import run_full_cleanup
import logging

router = APIRouter()

@router.post("/trigger-scraper")
async def trigger_scraper(limit: int = 20, source: str = "remotive"):
    """
    Endpoint admin pour déclencher manuellement la récupération de nouvelles offres.
    source: 'remotive', 'francetravail', ou 'jsearch'
    """
    try:
        if source == "francetravail":
            result = fetch_ft_jobs(limit=limit)
        elif source == "jsearch":
            result = fetch_jsearch_jobs(limit=limit)
        else:
            result = fetch_remotive_jobs(limit=limit)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {"message": f"Scraping terminé ({source})", "details": result}
    except Exception as e:
        logging.error(f"Erreur router scraper: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne de scraping.")


@router.post("/cleanup")
async def cleanup_offers():
    """Supprime les offres expirées (> 30 j) et efface les offres > 60 j."""
    try:
        result = run_full_cleanup()
        return {"message": "Nettoyage terminé", "details": result}
    except Exception as e:
        logging.error(f"Erreur cleanup: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du nettoyage.")
