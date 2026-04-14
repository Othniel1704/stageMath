from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging
import os
import re
import unicodedata

from dotenv import load_dotenv
from supabase import Client, create_client

from services.job_fetcher import is_in_france

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY", "")
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    logging.warning(f"Failed to initialize Supabase client for matching: {e}")
    supabase = None

FRENCH_CITIES = [
    "paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg",
    "montpellier", "bordeaux", "lille", "rennes", "reims", "toulon", "grenoble",
    "dijon", "angers", "nimes", "villeurbanne", "saint-etienne", "vincennes",
    "bezons", "cergy", "versailles", "creteil", "argenteuil", "montreuil",
    "ile-de-france", "idf", "banlieue", "region parisienne",
]

REMOTE_KEYWORDS = ["remote", "hybride", "teletravail", "distanciel", "anywhere", "worldwide"]


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text.strip().lower())


def get_supabase_client(user_token: Optional[str] = None) -> Optional[Client]:
    try:
        client = create_client(url, key)
        if user_token:
            client.postgrest.auth(user_token)
        return client
    except Exception as e:
        logging.error(f"Failed to initialize authenticated Supabase client: {e}")
        return None


def normalize_list(values: Any) -> List[str]:
    if isinstance(values, list):
        raw_values = values
    elif isinstance(values, str):
        raw_values = [part.strip() for part in values.split(",")]
    else:
        raw_values = []

    seen = set()
    normalized_values = []
    for value in raw_values:
        item = normalize_text(str(value))
        if item and item not in seen:
            seen.add(item)
            normalized_values.append(item)
    return normalized_values


def has_meaningful_embedding(embedding: Any) -> bool:
    if not isinstance(embedding, list) or not embedding:
        return False
    return any(abs(float(value)) > 1e-9 for value in embedding)


def prettify_skill(skill: str) -> str:
    return skill.replace("-", " ").replace("_", " ").title()


def build_excerpt(description: str, max_length: int = 220) -> str:
    cleaned = re.sub(r"\s+", " ", description or "").strip()
    if not cleaned:
        return "Description non disponible."
    if len(cleaned) <= max_length:
        return cleaned
    clipped = cleaned[: max_length - 1].rsplit(" ", 1)[0]
    return f"{clipped}…"


def extract_location_from_cv(raw_text: str) -> Optional[str]:
    text_lower = normalize_text(raw_text)
    for city in FRENCH_CITIES:
        if city in text_lower:
            return city.title()

    postal = re.search(r"\b(75|77|78|91|92|93|94|95)\d{0,3}\b", raw_text or "")
    if postal:
        return "Ile-de-France"
    return None


def score_to_tier(score: int) -> str:
    if score >= 80:
        return "excellent"
    if score >= 65:
        return "strong"
    if score >= 45:
        return "promising"
    return "explore"


def score_to_color(score: int) -> str:
    if score >= 75:
        return "success"
    if score >= 45:
        return "warning"
    return "error"


def location_score(candidate_location: Optional[str], job_location: str) -> int:
    if not candidate_location:
        return 25 if any(word in normalize_text(job_location) for word in REMOTE_KEYWORDS) else 0

    cand_loc_lower = normalize_text(candidate_location)
    job_loc_lower = normalize_text(job_location)

    if cand_loc_lower in ("france entiere", "france"):
        return 100 if is_in_france(job_location) else 15

    if any(word in job_loc_lower for word in REMOTE_KEYWORDS):
        return 80

    if cand_loc_lower and (cand_loc_lower in job_loc_lower or job_loc_lower in cand_loc_lower):
        return 100

    idf_keywords = ["paris", "ile-de-france", "idf", "92", "93", "94", "95", "77", "78", "91"]
    cand_in_idf = any(k in cand_loc_lower for k in idf_keywords)
    job_in_idf = any(k in job_loc_lower for k in idf_keywords)
    if cand_in_idf and job_in_idf:
        return 75

    return 0


def contract_score(preferred_contract: Optional[str], job_contract: Optional[str]) -> int:
    pref = normalize_text(preferred_contract)
    contract = normalize_text(job_contract)

    if not pref:
        return 60
    if not contract:
        return 35
    if pref in contract:
        return 100
    if (pref == "stage" and "alternance" in contract) or (pref == "alternance" and "stage" in contract):
        return 55
    if pref == "alternance" and "apprentissage" in contract:
        return 100
    return 0


def calculate_match_score_db(user_skills: str, job_description: str) -> int:
    if not user_skills or not job_description:
        return 0

    job_lower = normalize_text(job_description)
    skill_list = normalize_list(user_skills)
    score = 0

    for skill in skill_list:
        if len(skill) > 2 and skill in job_lower:
            score += 12

    return min(score, 100)


def detect_missing_info(raw_text: str, candidate_location: Optional[str]) -> List[str]:
    missing = []
    if not candidate_location:
        missing.append("location")

    contract_hints = ["alternance", "stage", "cdi", "cdd", "freelance", "apprentissage"]
    has_contract = any(h in normalize_text(raw_text) for h in contract_hints)
    if not has_contract:
        missing.append("contract_type")
    return missing


def build_match_reasons(
    explicit_skill_matches: List[str],
    semantic_score: int,
    location_component: int,
    contract_component: int,
    location_value: str,
    contract_value: str,
) -> List[str]:
    reasons: List[str] = []

    if explicit_skill_matches:
        preview = ", ".join(prettify_skill(skill) for skill in explicit_skill_matches[:3])
        reasons.append(f"Competences detectees en commun: {preview}")

    if semantic_score >= 70:
        reasons.append("Le contenu de l'offre est tres proche de votre profil")
    elif semantic_score >= 50:
        reasons.append("Le profil correspond bien aux missions principales")

    if location_component >= 75 and location_value:
        reasons.append(f"Localisation compatible avec votre preference: {location_value}")
    elif location_component >= 75:
        reasons.append("Offre accessible en remote ou tres proche geographiquement")

    if contract_component >= 100 and contract_value:
        reasons.append(f"Contrat parfaitement aligne: {contract_value}")

    return reasons[:4]


def build_job_payload(
    job: Dict[str, Any],
    final_score: int,
    semantic_score: int,
    skills_score: int,
    location_component: int,
    contract_component: int,
    explicit_skill_matches: List[str],
    effective_location: str,
    preferred_contract: Optional[str],
) -> Dict[str, Any]:
    title = job.get("title") or "Offre sans titre"
    company_name = job.get("company_name") or "Entreprise confidentielle"
    location = job.get("location") or "Non specifie"
    contract_type = job.get("contract_type") or "Non specifie"
    description = job.get("description") or ""

    return {
        "id": job["id"],
        "title": title,
        "company_name": company_name,
        "location": location,
        "url": job.get("url"),
        "contract_type": contract_type,
        "match_score": final_score,
        "skills_required": job.get("skills_required", []) or [],
        "source": job.get("source", "StageMatch"),
        "score_color": score_to_color(final_score),
        "score_label": score_to_tier(final_score),
        "summary": build_excerpt(description),
        "matching_reasons": build_match_reasons(
            explicit_skill_matches,
            semantic_score,
            location_component,
            contract_component,
            effective_location,
            preferred_contract or "",
        ),
        "score_breakdown": {
            "semantic": semantic_score,
            "skills": skills_score,
            "location": location_component,
            "contract": contract_component,
        },
        "matched_skills": [prettify_skill(skill) for skill in explicit_skill_matches[:6]],
    }


async def find_matching_jobs(
    user_id: str,
    user_location: Optional[str] = None,
    preferred_contract: Optional[str] = None,
    user_token: Optional[str] = None,
    limit: int = 20,
) -> dict:
    if not supabase:
        raise Exception("Supabase client not initialized")

    try:
        client = get_supabase_client(user_token) or supabase
        profile_result = (
            client.table("profiles")
            .select("cv_embedding, competences_extraites, location, preferred_contract")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile_result.data:
            return empty_match_response(limit, user_location or "France entiere")

        profile = profile_result.data[0]
        user_embedding = profile.get("cv_embedding")
        profile_location = profile.get("location")
        profile_contract = profile.get("preferred_contract")
        effective_location = user_location or profile_location or "France entiere"
        effective_contract = preferred_contract or profile_contract

        if not has_meaningful_embedding(user_embedding):
            logging.warning(f"Pas d'embedding pour l'utilisateur {user_id}, fallback vers ancien systeme")
            return await find_matching_jobs_fallback(
                user_id=user_id,
                user_location=effective_location,
                preferred_contract=effective_contract,
                user_token=user_token,
                limit=limit,
            )

        user_skills = normalize_list(profile.get("competences_extraites", ""))

        result = (
            client.table("job_offers")
            .select("id, title, company_name, location, url, contract_type, description, skills_required, embedding, source, created_at")
            .order("created_at", desc=True)
            .limit(250)
            .execute()
        )

        if not result.data:
            return empty_match_response(limit, effective_location)

        from services.embedding_service import cosine_similarity

        matched_jobs = []
        for job in result.data:
            description = job.get("description") or ""
            job_embedding = job.get("embedding", [])
            job_skills = normalize_list(job.get("skills_required", []))

            if has_meaningful_embedding(job_embedding) and has_meaningful_embedding(user_embedding):
                similarity = cosine_similarity(user_embedding, job_embedding)
                semantic_score = max(0, min(int(similarity * 100), 100))
            else:
                semantic_score = calculate_match_score_db(",".join(user_skills), description)

            explicit_skill_matches = [skill for skill in job_skills if any(skill in user_skill or user_skill in skill for user_skill in user_skills)]

            if job_skills:
                skills_score = int((len(explicit_skill_matches) / len(job_skills)) * 100)
            else:
                description_hits = [skill for skill in user_skills if len(skill) > 2 and skill in normalize_text(description)]
                explicit_skill_matches = explicit_skill_matches or description_hits[:6]
                skills_score = min(len(description_hits) * 18, 100)

            location_component = location_score(effective_location, job.get("location", ""))
            contract_component = contract_score(effective_contract, job.get("contract_type"))

            final_score = int(
                (semantic_score * 0.45)
                + (skills_score * 0.30)
                + (location_component * 0.15)
                + (contract_component * 0.10)
            )
            final_score = max(0, min(final_score, 100))

            if final_score < 20 and semantic_score < 15 and skills_score == 0:
                continue

            matched_jobs.append(
                build_job_payload(
                    job=job,
                    final_score=final_score,
                    semantic_score=semantic_score,
                    skills_score=skills_score,
                    location_component=location_component,
                    contract_component=contract_component,
                    explicit_skill_matches=explicit_skill_matches,
                    effective_location=effective_location,
                    preferred_contract=effective_contract,
                )
            )

        matched_jobs.sort(
            key=lambda item: (
                item["match_score"],
                item["score_breakdown"]["skills"],
                item["score_breakdown"]["semantic"],
            ),
            reverse=True,
        )
        limited_jobs = matched_jobs[:limit]

        return {
            "jobs": limited_jobs,
            "total_count": len(matched_jobs),
            "page": 1,
            "page_size": limit,
            "has_more": len(matched_jobs) > limit,
            "mobility_added_by_default": False,
            "location_used": effective_location,
        }

    except Exception as e:
        logging.error(f"Erreur matching vectoriel: {e}")
        return await find_matching_jobs_fallback(
            user_id=user_id,
            user_location=user_location,
            preferred_contract=preferred_contract,
            user_token=user_token,
            limit=limit,
        )


async def find_matching_jobs_fallback(
    user_id: str,
    user_location: Optional[str] = None,
    preferred_contract: Optional[str] = None,
    user_token: Optional[str] = None,
    limit: int = 20,
) -> dict:
    if not supabase:
        raise Exception("Supabase client not initialized")

    try:
        client = get_supabase_client(user_token) or supabase
        profile_result = (
            client.table("profiles")
            .select("competences_extraites, location, preferred_contract")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile_result.data:
            return empty_match_response(limit, user_location or "France entiere")

        profile = profile_result.data[0]
        user_competences = profile.get("competences_extraites", "")
        effective_location = user_location or profile.get("location") or "France entiere"
        effective_contract = preferred_contract or profile.get("preferred_contract")

        result = (
            client.table("job_offers")
            .select("id, title, company_name, location, url, contract_type, description, skills_required, source, created_at")
            .order("created_at", desc=True)
            .limit(120)
            .execute()
        )

        if not result.data:
            return empty_match_response(limit, effective_location)

        user_skill_list = normalize_list(user_competences)
        matched_jobs = []

        for job in result.data:
            description = job.get("description", "")
            job_skills = normalize_list(job.get("skills_required", []))
            explicit_skill_matches = [skill for skill in job_skills if any(skill in user_skill or user_skill in skill for user_skill in user_skill_list)]

            semantic_score = calculate_match_score_db(user_competences, description)
            if job_skills:
                skills_score = int((len(explicit_skill_matches) / len(job_skills)) * 100)
            else:
                description_hits = [skill for skill in user_skill_list if skill and skill in normalize_text(description)]
                explicit_skill_matches = explicit_skill_matches or description_hits[:6]
                skills_score = min(len(description_hits) * 18, 100)

            location_component = location_score(effective_location, job.get("location", ""))
            contract_component = contract_score(effective_contract, job.get("contract_type"))
            final_score = int(
                (semantic_score * 0.45)
                + (skills_score * 0.30)
                + (location_component * 0.15)
                + (contract_component * 0.10)
            )
            final_score = max(0, min(final_score, 100))

            if final_score < 15 and not explicit_skill_matches:
                continue

            matched_jobs.append(
                build_job_payload(
                    job=job,
                    final_score=final_score,
                    semantic_score=semantic_score,
                    skills_score=skills_score,
                    location_component=location_component,
                    contract_component=contract_component,
                    explicit_skill_matches=explicit_skill_matches,
                    effective_location=effective_location,
                    preferred_contract=effective_contract,
                )
            )

        matched_jobs.sort(key=lambda item: item["match_score"], reverse=True)
        limited_jobs = matched_jobs[:limit]

        return {
            "jobs": limited_jobs,
            "total_count": len(matched_jobs),
            "page": 1,
            "page_size": limit,
            "has_more": len(matched_jobs) > limit,
            "mobility_added_by_default": False,
            "location_used": effective_location,
        }

    except Exception as e:
        logging.error(f"Erreur fallback matching: {e}")
        raise Exception(f"Erreur lors du matching: {str(e)}")


def empty_match_response(limit: int, location_used: str) -> dict:
    return {
        "jobs": [],
        "total_count": 0,
        "page": 1,
        "page_size": limit,
        "has_more": False,
        "mobility_added_by_default": False,
        "location_used": location_used,
    }
