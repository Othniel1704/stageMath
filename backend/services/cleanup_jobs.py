"""
Job cron : nettoyage des offres expirées dans Supabase.
À exécuter planifié (ex: via `python -m backend.services.cleanup_jobs` chaque nuit).
Peut aussi être appelé via un endpoint admin.
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

try:
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL", ""),
        os.environ.get("SUPABASE_ANON_KEY", "")
    )
except Exception as e:
    logging.error(f"Supabase init failed: {e}")
    supabase = None


def mark_old_offers_expired(days_old: int = 30) -> dict:
    """
    Marque les offres sans date d'expiration `expires_at` comme expirées
    si elles ont été créées il y a plus de `days_old` jours.
    """
    if not supabase:
        return {"error": "Supabase non initialisé"}

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
    cutoff_str = cutoff.isoformat()

    try:
        # Récupérer les offres trop vieilles
        res = supabase.table("job_offers") \
            .select("id, title, created_at") \
            .lt("created_at", cutoff_str) \
            .is_("expires_at", "null") \
            .execute()

        old_offers = res.data
        count = len(old_offers)

        if count > 0:
            ids = [o["id"] for o in old_offers]
            # Mettre à jour expires_at pour les signaler comme expirées
            supabase.table("job_offers") \
                .update({"expires_at": cutoff_str}) \
                .in_("id", ids) \
                .execute()
            logging.info(f"[Cleanup] {count} offres marquées comme expirées (> {days_old} jours)")

        return {
            "status": "success",
            "expired_marked": count,
            "cutoff_date": cutoff_str
        }

    except Exception as e:
        logging.error(f"Erreur cleanup: {e}")
        return {"error": str(e)}


def delete_expired_offers() -> dict:
    """Supprime définitivement les offres déjà marquées comme expirées."""
    if not supabase:
        return {"error": "Supabase non initialisé"}
    try:
        now_str = datetime.now(timezone.utc).isoformat()
        res = supabase.table("job_offers") \
            .delete() \
            .lt("expires_at", now_str) \
            .execute()
        deleted = len(res.data) if res.data else 0
        logging.info(f"[Cleanup] {deleted} offres supprimées définitivement")
        return {"status": "success", "deleted": deleted}
    except Exception as e:
        logging.error(f"Erreur suppression: {e}")
        return {"error": str(e)}


def run_full_cleanup() -> dict:
    """
    Pipeline complet de nettoyage :
    1. Marque les offres > 30 jours comme expirées
    2. Supprime les offres > 60 jours déjà marquées
    """
    step1 = mark_old_offers_expired(days_old=30)
    step2 = delete_expired_offers()
    return {"mark_expired": step1, "delete_old": step2}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🧹 Lancement du nettoyage des offres expirées...")
    result = run_full_cleanup()
    print("✅ Résultat:", result)
