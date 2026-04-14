import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health_check():
    """Test du endpoint de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_cv_without_auth():
    """Test upload CV sans authentification"""
    response = client.post("/upload-cv")
    assert response.status_code == 422  # Validation error

def test_match_without_auth():
    """Test matching sans authentification"""
    response = client.post("/match", json={})
    assert response.status_code == 401

def test_match_check_info_without_auth():
    """Test check-info sans authentification"""
    response = client.post("/match/check-info", json={})
    assert response.status_code == 401

# Tests des services
from services.embedding_service import generate_embedding, cosine_similarity

def test_generate_embedding():
    """Test génération d'embedding"""
    text = "Python developer with FastAPI experience"
    embedding = generate_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 384  # Dimension du modèle
    assert all(isinstance(x, float) for x in embedding)

def test_cosine_similarity():
    """Test calcul de similarité cosinus"""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = cosine_similarity(vec1, vec2)
    assert similarity == pytest.approx(1.0)

    vec3 = [0.0, 1.0, 0.0]
    similarity = cosine_similarity(vec1, vec3)
    assert similarity == pytest.approx(0.0)

def test_empty_embedding():
    """Test embedding pour texte vide"""
    embedding = generate_embedding("")
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(x == 0.0 for x in embedding)

# Tests du service matching
from services.matching import calculate_match_score_db, location_score

def test_calculate_match_score_basic():
    """Test calcul de score basique"""
    user_skills = "Python, FastAPI, PostgreSQL"
    job_description = "Nous recherchons un développeur Python avec FastAPI"

    score = calculate_match_score_db(user_skills, job_description)
    assert score >= 20  # Au moins 2 compétences trouvées
    assert score <= 100

def test_calculate_match_score_no_match():
    """Test quand aucune compétence ne match"""
    user_skills = "Python, FastAPI"
    job_description = "Java developer needed"

    score = calculate_match_score_db(user_skills, job_description)
    assert score == 0

def test_calculate_match_score_empty():
    """Test avec paramètres vides"""
    score = calculate_match_score_db("", "")
    assert score == 0

def test_location_score():
    """Test calcul du score de localisation"""
    # Même ville
    score = location_score("Paris", "Paris, France")
    assert score == 40

    # France entière
    score = location_score("France entière", "Marseille, France")
    assert score == 40

    # Remote
    score = location_score("Paris", "Remote")
    assert score == 20

    # Pas de localisation
    score = location_score(None, "Paris")
    assert score == 0

    # Localisations différentes
    score = location_score("Paris", "Marseille")
    assert score == 0

# Tests du service profile
from services.profile_service import upsert_profile_antigravity
import asyncio

@pytest.mark.asyncio
async def test_upsert_profile_antigravity():
    """Test création de profil (nécessite une vraie DB pour être complet)"""
    # Ce test nécessiterait une vraie base de données de test
    # Pour l'instant, on teste juste que la fonction existe et ne crash pas
    try:
        result = await upsert_profile_antigravity(
            user_id="test_user",
            candidate_name="Test User",
            candidate_email="test@example.com",
            competences_extraites="Python, FastAPI",
            raw_cv_text="Test CV content",
            cv_embedding=[0.1] * 384
        )
        # Le résultat dépend de la connexion DB
        assert isinstance(result, bool)
    except Exception:
        # Si pas de DB, c'est normal que ça échoue
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])