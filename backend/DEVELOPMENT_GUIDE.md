# Guide du Développeur - StageMatch Antigravity

## Vue d'ensemble

Ce guide explique comment développer, tester et déployer le système **Antigravity** de StageMatch.

## 🏗️ Architecture

### Composants Principaux

```
backend/
├── main.py                 # Point d'entrée FastAPI
├── routers/               # Endpoints API
│   ├── upload.py         # Upload et analyse CV
│   ├── match.py          # Matching des offres
│   ├── applications.py   # Gestion candidatures
│   └── profile.py        # Profil utilisateur
├── services/             # Logique métier
│   ├── ai_parser.py      # Analyse IA des CV
│   ├── matching.py       # Algorithmes de matching
│   └── profile_service.py # Gestion profils
├── scripts/              # Outils et utilitaires
│   ├── migrate_antigravity.py    # Migration DB
│   ├── test_antigravity.py       # Tests fonctionnels
│   ├── cleanup_antigravity.py    # Nettoyage fichiers
│   ├── monitor_antigravity.py    # Monitoring système
│   └── scheduler_antigravity.py  # Tâches planifiées
└── db/                  # Schéma base de données
    └── antigravity_migration.sql
```

## 🚀 Démarrage Rapide

### 1. Configuration de l'environnement

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Variables d'environnement

Copiez le fichier de configuration :
```bash
cp .env.antigravity .env
```

Éditez `.env` avec vos vraies credentials Supabase.

### 3. Migration de base de données

```bash
python scripts/migrate_antigravity.py
```

### 4. Démarrage du serveur

```bash
# Via script
./start_antigravity.bat  # Windows
./start_antigravity.sh   # Linux/Mac

# Ou directement
uvicorn main:app --reload
```

## 🧪 Tests et Validation

### Tests Fonctionnels

```bash
# Tester tout le système
python scripts/test_antigravity.py path/to/test/cv.pdf

# Tester uniquement certains endpoints
python -m pytest tests/ -v
```

### Monitoring

```bash
# Monitoring continu
python scripts/monitor_antigravity.py --continuous

# Rapport unique
python scripts/monitor_antigravity.py --report-file report.json
```

### Nettoyage

```bash
# Nettoyage avec aperçu
python scripts/cleanup_antigravity.py --dry-run

# Nettoyage réel
python scripts/cleanup_antigravity.py
```

## 🔧 Développement

### Structure des Endpoints

Tous les endpoints suivent le pattern REST :

```python
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/endpoint")
async def endpoint_function(
    data: RequestModel,
    current_user: dict = Depends(get_current_user)
):
    # Logique métier
    result = await service.process(data, current_user)
    return ResponseModel(**result)
```

### Gestion des Erreurs

Utilisez les exceptions FastAPI standard :

```python
from fastapi import HTTPException

# Erreur 400 - Bad Request
raise HTTPException(status_code=400, detail="Invalid input")

# Erreur 404 - Not Found
raise HTTPException(status_code=404, detail="Resource not found")

# Erreur 500 - Internal Server Error
raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging

Utilisez le logger standard :

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Operation successful")
logger.warning("Potential issue detected")
logger.error("Operation failed", exc_info=True)
```

## 📊 Base de Données

### Schéma Antigravity

```sql
-- Profils utilisateurs avec stockage local
ALTER TABLE profiles ADD COLUMN chemin_acces_local TEXT;
ALTER TABLE profiles ADD COLUMN competences_extraites TEXT;

-- Offres d'emploi avec scoring
ALTER TABLE job_offers ADD COLUMN statut TEXT DEFAULT 'active';
ALTER TABLE job_offers ADD COLUMN score_matching INTEGER;

-- Suivi des candidatures
CREATE TABLE saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    job_offer_id INTEGER REFERENCES job_offers(id),
    status TEXT DEFAULT 'Enregistré',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Fonctions PostgreSQL

```sql
-- Vérification type d'offre
CREATE FUNCTION is_stage_or_alternance(contract_type TEXT) RETURNS BOOLEAN;

-- Calcul score de matching
CREATE FUNCTION calculate_match_score(
    job_description TEXT,
    user_skills TEXT
) RETURNS INTEGER;
```

## 🔒 Sécurité

### Authentification

Tous les endpoints protégés utilisent Supabase Auth :

```python
from ..dependencies import get_current_user

@router.get("/protected")
async def protected_endpoint(
    current_user: dict = Depends(get_current_user)
):
    return {"user_id": current_user["id"]}
```

### Validation des Entrées

Utilisez Pydantic pour la validation :

```python
from pydantic import BaseModel, validator

class UploadRequest(BaseModel):
    file: UploadFile

    @validator('file')
    def validate_file(cls, v):
        if not v.filename.endswith(('.pdf', '.doc', '.docx')):
            raise ValueError('Invalid file type')
        return v
```

## 📈 Performance

### Optimisations

1. **One-shot extraction** : Analyse IA une seule fois
2. **Stockage local** : Évite les relectures répétées
3. **Indexation DB** : Requêtes optimisées
4. **Cache** : Résultats fréquemment utilisés

### Métriques à Surveiller

- Temps de réponse des endpoints
- Utilisation CPU/Mémoire
- Taille du stockage temporaire
- Taux de succès des analyses IA

## 🚀 Déploiement

### Environnements

- **Développement** : Configuration locale
- **Staging** : Test avant production
- **Production** : Configuration optimisée

### Variables d'environnement par environnement

```bash
# Développement
ENVIRONMENT=development
DEBUG=true

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### Health Checks

Endpoints de monitoring :

```bash
# Health check basique
GET /health

# Métriques détaillées
GET /metrics

# Status des services
GET /status
```

## 🤝 Contribution

### Processus de Développement

1. **Créer une branche** : `git checkout -b feature/nom-fonctionnalite`
2. **Développer** : Implémenter la fonctionnalité
3. **Tester** : Tests unitaires et fonctionnels
4. **Documenter** : Mettre à jour la documentation
5. **Commit** : Messages clairs et concis
6. **Pull Request** : Description détaillée

### Standards de Code

- **PEP 8** : Style Python standard
- **Type hints** : Annotation des types
- **Docstrings** : Documentation des fonctions
- **Tests** : Couverture minimale 80%

### Reviews de Code

- Vérifier la sécurité
- Valider les performances
- Contrôler la documentation
- Tester la régression

## 📞 Support

### Ressources

- **Documentation API** : `http://localhost:8000/docs`
- **Logs** : `logs/antigravity_*.log`
- **Rapports** : `reports/`

### Debugging

1. Vérifier les logs
2. Tester les endpoints individuellement
3. Utiliser le debugger VS Code
4. Monitorer les ressources système

---

*Guide du Développeur - StageMatch Antigravity*