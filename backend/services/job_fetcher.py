import requests
import json
import logging
import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv
from services.cache_service import cache_get, cache_set
from services.retry_service import retry_on_failure
from services.embedding_service import generate_job_embedding

# --- CONFIGURATION ---
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY", "")
ft_token: str = os.environ.get("FRANCE_TRAVAIL_TOKEN", "")
jsearch_key: str = os.environ.get("JSEARCH_KEY", "")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    logging.warning(f"Failed to initialize Supabase client: {e}")
    supabase = None

# --- FONCTIONS UTILITAIRES ---

def clean_html(raw_html):
    """Nettoie les balises HTML des descriptions."""
    if not raw_html: return ""
    clean = re.sub('<[^<]+>', '', raw_html)
    return clean.replace('\n', ' ').strip()

def is_in_france(location_string):
    """Verifie si la localisation concerne la France."""
    if not location_string:
        return False
    loc = location_string.lower()
    return "france" in loc or "75" in loc or "paris" in loc or "lyon" in loc

def is_valid_contract(contract_string):
    """Filtre pour ne garder QUE les stages et alternances."""
    if not contract_string:
        return False
    c = contract_string.lower()
    valid_keywords = ["stage", "alternance", "apprentissage", "professionnalisation", "internship", "apprentice", "trainee"]
    invalid_keywords = ["cdi", "cdd", "freelance", "independant"]
    
    if any(kw in c for kw in invalid_keywords):
        return False
    return any(kw in c for kw in valid_keywords)

# --- SCRAPPING ---

def fetch_ft_jobs(limit=10, user_mobility=None, use_cache=True):
    """Desactive car necessite un token valide (401)."""
    logging.info("Source France Travail ignoree (Token invalide)")
    return {"source": "FT", "inserted": 0, "status": "skipped"}

def _fetch_remotive_api(api_url: str):
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_remotive_jobs(limit=15, user_mobility=None, use_cache=True):
    if not supabase: return {"error": "Supabase non configure"}
    
    api_url = f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
    try:
        data = _fetch_remotive_api(api_url)
        jobs = data.get('jobs', [])
        inserted_count = 0
        for job in jobs:
            raw_loc = job.get('candidate_required_location', '')
            if not is_in_france(raw_loc): continue
            
            offer_data = {
                "title": job.get('title'),
                "company_name": job.get('company_name'),
                "location": raw_loc if raw_loc else "France entiere",
                "description": clean_html(job.get('description'))[:1000],
                "url": job.get('url'),
                "source": "Remotive",
                "contract_type": job.get('job_type', 'Autre'),
                "skills_required": job.get('tags', [])
            }
            offer_data["embedding"] = generate_job_embedding(offer_data)
            
            try:
                existing = supabase.table('job_offers').select('id').eq('url', offer_data['url']).execute()
                if not existing.data:
                    supabase.table('job_offers').insert(offer_data).execute()
                    inserted_count += 1
            except Exception: pass
        return {"source": "Remotive", "inserted": inserted_count}
    except Exception as e:
        return {"error": str(e), "source": "Remotive"}

def fetch_jsearch_jobs(query="developer jobs in France", limit=10):
    if not supabase: return {"error": "Supabase non configure"}
    
    api_url = "https://jsearch.p.rapidapi.com/search"
    querystring = {"query": query, "page": "1", "num_pages": "1", "country": "fr"}
    headers = {"x-rapidapi-key": jsearch_key, "x-rapidapi-host": "jsearch.p.rapidapi.com"}

    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        jobs = data.get('data', [])
        inserted_count = 0
        for job in jobs[:limit]:
            raw_loc = job.get('job_location', 'France')
            if not is_in_france(raw_loc): continue
            
            offer_data = {
                "title": job.get('job_title'),
                "company_name": job.get('employer_name'),
                "location": raw_loc,
                "description": clean_html(job.get('job_description'))[:1000],
                "url": job.get('job_apply_link'),
                "source": "JSearch",
                "contract_type": job.get('job_employment_type', 'Autre'),
                "skills_required": []
            }
            offer_data["embedding"] = generate_job_embedding(offer_data)
            try:
                existing = supabase.table('job_offers').select('id').eq('url', offer_data['url']).execute()
                if not existing.data:
                    supabase.table('job_offers').insert(offer_data).execute()
                    inserted_count += 1
            except Exception: pass
        return {"source": "JSearch", "query": query, "inserted": inserted_count}
    except Exception as e:
        return {"error": str(e), "source": "JSearch"}

if __name__ == "__main__":
    print("Démarrage du scraping intensif...")
    
    # 1. Remotive
    print("\n[1/2] Scraping Remotive...")
    print(fetch_remotive_jobs(limit=100))
    
    # 2. JSearch (Multi-requetes)
    print("\n[2/2] Scraping JSearch (Multi-requetes)...")
    queries = [
        "developpeur react france",
        "stage informatique paris",
        "alternance developpeur lyon",
        "developpeur python france",
        "developpeur javascript alternance"
    ]
    for q in queries:
        print(f"  - {q}...")
        print(fetch_jsearch_jobs(query=q, limit=20))
    
    print("\nScraping termine.")