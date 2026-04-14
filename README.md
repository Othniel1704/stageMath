# stageMath

StageMatch est une application de type jobboard orientée vers la recherche de stages et d'alternances.
Le projet combine un backend Python/FastAPI avec un frontend Next.js pour offrir un parcours candidat complet : dépôt de CV, extraction de compétences, matching d'offres, suivi des candidatures.

## Architecture

- `backend/` : API FastAPI, traitement de CV, matching, services métier, gestion des candidatures.
- `frontend/` : application Next.js moderne avec interface utilisateur pour le candidat.
- `backend/db/` : fichiers de schéma et migrations SQL.

## Fonctionnalités principales

- upload de CV en PDF/image
- extraction automatique de données et compétences
- création et mise à jour de profil candidat
- matching des offres avec score de pertinence
- catalogue d'offres
- suivi des candidatures (à postuler plus tard / postulé)
- administration et endpoints API dédiés

## Stack technique

- Backend : Python, FastAPI, Uvicorn, Supabase, SQLAlchemy, Alembic
- Frontend : Next.js, React, TypeScript, Supabase JS
- IA / parsing : spaCy, Tesseract OCR, pdfplumber, sentence-transformers

## Prérequis

- Python 3.11+ ou 3.12+
- Node.js 18+ / npm
- Accès à un projet Supabase pour les variables d'environnement

## Installation et exécution

### Backend

1. Ouvrir un terminal dans `backend/`
2. Créer un environnement virtuel :

```powershell
python -m venv venv
```

3. Activer l'environnement :

```powershell
venv\Scripts\activate
```

4. Installer les dépendances :

```powershell
pip install -r requirements.txt
```

5. Configurer les variables d'environnement :

- Copier le fichier de configuration existant si nécessaire
- Modifier `backend/.env` ou `backend/.env.antigravity`

Variables attendues :

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `ENVIRONMENT`

6. Lancer le backend :

```powershell
uvicorn main:app --reload
```

L'API sera disponible sur `http://localhost:8000`.
La documentation interactive est sur `http://localhost:8000/docs`.

### Frontend

1. Ouvrir un terminal dans `frontend/`
2. Installer les dépendances :

```powershell
npm install
```

3. Démarrer le serveur de développement :

```powershell
npm run dev
```

L'interface sera disponible sur `http://localhost:3000`.

## Commandes utiles

- `npm run dev` : démarrer le frontend en mode développement
- `npm run build` : construire le frontend
- `npm run start` : lancer le frontend buildé
- `uvicorn main:app --reload` : lancer l'API backend
- `pytest` ou `python -m pytest` : exécuter les tests Python

## Organisation du projet

### Backend

- `main.py` : point d'entrée FastAPI
- `routers/` : routes API (`upload`, `match`, `profile`, `applications`, `admin`, `jobs`)
- `services/` : logique métier et traitement des données
- `scripts/` : outils de migration, tests et maintenance
- `db/` : scripts SQL et schémas de base de données

### Frontend

- `src/app/` : pages et composants de l'application
- `src/lib/supabase.ts` : configuration du client Supabase

## Notes

- Vérifier que les fichiers `.gitignore` sont bien configurés pour ignorer les dépendances et fichiers locaux temporaires.
- Ne pas partager les secrets Supabase ou les fichiers `.env` publics.
- Ce projet suppose un backend et un frontend exécutés séparément.

---

## Pour aller plus loin

1. Configurer Supabase avec les tables nécessaires
2. Vérifier les endpoints `/api` exposés par le backend
3. Connecter le frontend au backend et aux données utilisateur
4. Ajouter des tests supplémentaires pour le matching et l'import de CV

