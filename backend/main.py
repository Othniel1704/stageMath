import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

# Importer les routers
from routers import upload, data, match, profile, applications, admin, jobs
from utils.logger import logger

load_dotenv()

app = FastAPI(title="StageMatch API", version="1.0.0")

# Configuration CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173", # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Initialization
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY", "")
try:
    supabase: Client = create_client(url, key)
    logger.info("Connexion Supabase établie")
except Exception as e:
    logger.error(f"Erreur connexion Supabase: {e}")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(data.router, prefix="/api/admin", tags=["Admin Data"])
app.include_router(match.router, prefix="/api", tags=["Matching"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Monitoring"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Démarrage de l'API JobBoard")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API StageMatch"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
