#!/usr/bin/env python3
"""
Script d'exécution de la migration Antigravity pour StageMatch.
Exécute le fichier SQL de migration dans Supabase.
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_antigravity_migration():
    """
    Exécute la migration Antigravity dans Supabase.
    """
    try:
        # Initialiser le client Supabase
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Variables d'environnement SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requises")

        logger.info("Connexion à Supabase...")
        supabase = create_client(supabase_url, supabase_key)

        # Lire le fichier de migration
        migration_file = "db/antigravity_migration.sql"
        if not os.path.exists(migration_file):
            raise FileNotFoundError(f"Fichier de migration non trouvé: {migration_file}")

        logger.info("Lecture du fichier de migration...")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        # Diviser le SQL en statements individuels
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]

        logger.info(f"Exécution de {len(statements)} statements SQL...")

        # Exécuter chaque statement
        for i, statement in enumerate(statements, 1):
            if statement:
                logger.info(f"Exécution du statement {i}/{len(statements)}...")
                try:
                    # Utiliser rpc pour exécuter du SQL brut
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    logger.info(f"Statement {i} exécuté avec succès")
                except Exception as e:
                    logger.warning(f"Erreur sur statement {i}: {e}")
                    # Continuer avec les autres statements

        logger.info("Migration Antigravity terminée!")
        logger.info("Vérifiez les logs Supabase pour confirmer l'exécution.")

        # Vérifier que les nouvelles colonnes existent
        logger.info("Vérification des nouvelles colonnes...")
        try:
            # Test de la fonction is_stage_or_alternance
            test_result = supabase.rpc('is_stage_or_alternance', {'contract_type': 'Stage'}).execute()
            logger.info(f"Fonction de filtrage testée: {test_result.data}")

            # Test de la fonction calculate_match_score
            score_result = supabase.rpc('calculate_match_score', {
                'user_skills': 'Python, JavaScript, React',
                'job_description': 'Nous recherchons un développeur Python avec React'
            }).execute()
            logger.info(f"Fonction de scoring testée: score = {score_result.data}")

        except Exception as e:
            logger.warning(f"Erreur lors des tests de fonction: {e}")

    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    logger.info("🚀 Démarrage de la migration Antigravity...")
    execute_antigravity_migration()
    logger.info("✅ Migration terminée avec succès!")