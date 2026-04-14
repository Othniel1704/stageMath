from sentence_transformers import SentenceTransformer
import logging
import numpy as np
from typing import List, Dict, Any

# Charger le modèle au démarrage (une seule fois)
try:
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    logging.info("Modèle d'embeddings chargé avec succès")
except Exception as e:
    logging.error(f"Erreur chargement modèle embeddings: {e}")
    model = None

def generate_embedding(text: str) -> List[float]:
    """
    Génère un embedding vectoriel à partir de texte.
    Retourne un vecteur de 384 dimensions.
    """
    if not text or len(text.strip()) == 0:
        return [0.0] * 384  # Vecteur nul par défaut

    if not model:
        logging.warning("Modèle d'embeddings non disponible")
        return [0.0] * 384

    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logging.error(f"Erreur génération embedding: {e}")
        return [0.0] * 384

def generate_job_embedding(job: Dict[str, Any]) -> List[float]:
    """
    Crée un embedding pour une offre d'emploi en combinant :
    - Titre
    - Description
    - Compétences requises
    """
    title = job.get('title', '')
    description = job.get('description', '')
    skills = ' '.join(job.get('skills_required', []))

    combined_text = f"{title} {description} {skills}"
    return generate_embedding(combined_text)

def generate_cv_embedding(profile_data: Dict[str, Any]) -> List[float]:
    """
    Crée un embedding pour un profil candidat en combinant :
    - Texte brut du CV
    - Compétences extraites
    """
    raw_text = profile_data.get('raw_cv_text', '')
    skills = profile_data.get('competences_extraites', '')

    combined_text = f"{raw_text} {skills}"
    return generate_embedding(combined_text)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs
    """
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
    except Exception as e:
        logging.error(f"Erreur calcul similarité: {e}")
        return 0.0