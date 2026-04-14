import spacy
import pytesseract
from PIL import Image, ImageEnhance
import io
import logging
import os
import re

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdfplumber non installé. Les PDFs seront ignorés.")

# Configuration Tesseract pour Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    logging.warning("Modèle spaCy 'fr_core_news_sm' non trouvé. NLP désactivé.")
    nlp = None

SKILL_KEYWORDS = [
    # Langages
    "python", "javascript", "typescript", "java", "php", "c++", "c#", "ruby", "go", "rust", "kotlin", "swift", "c", "objective-c", "dart", "scala", "clojure", "haskell",
    # Frontend
    "react", "react.js", "next.js", "vue", "vue.js", "angular", "tailwind", "sass", "html", "css", "bootstrap", "nuxt", "gatsby", "redux", "jquery", "material ui", "chakra ui",
    # Backend
    "fastapi", "django", "flask", "node.js", "express", "laravel", "spring", "symfony", "rails", "asp.net", ".net", ".net core", "dotnet", "nest.js", "graphql", "apollo",
    # Data / IA
    "sql", "postgresql", "mysql", "mongodb", "redis", "nosql", "machine learning", "deep learning", "ia", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "data science", "nlp", "vision", "big data", "spark", "hadoop",
    # DevOps / Outils
    "git", "github", "gitlab", "docker", "kubernetes", "linux", "bash", "ci/cd", "jenkins", "terraform", "ansible", "aws", "azure", "gcp", "heroku", "vercel", "netlify",
    # Méthodes
    "agile", "scrum", "kanban", "rest", "api", "graphql", "microservices", "tdd", "bdd", "design patterns", "architecture",
    # Réseau / Sys / Autre
    "active directory", "windows server", "ssms", "vs code", "firebase", "supabase", "postman", "figma", "notion", "jira", "office", "excel", "cybersecurity", "security",
]

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrait le texte directement depuis un PDF avec pdfplumber (pas d'OCR nécessaire)."""
    if not PDF_SUPPORT:
        return "Erreur : pdfplumber non installé. Impossible de lire le PDF."
    try:
        pages_text = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
        full_text = "\n".join(pages_text)
        return full_text if full_text.strip() else "Aucun texte extrait du PDF."
    except Exception as e:
        logging.error(f"Erreur pdfplumber: {e}")
        return f"Erreur lecture PDF: {str(e)}"

def extract_text_from_image(image_bytes: bytes) -> str:
    """OCR Tesseract avec prétraitement d'image pour les formats PNG/JPG."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('L')
        width, height = image.size
        if width < 2500:
            image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        image = ImageEnhance.Contrast(image).enhance(1.8)
        image = ImageEnhance.Sharpness(image).enhance(1.5)

        tessdata_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tessdata'))
        os.environ['TESSDATA_PREFIX'] = tessdata_dir

        text = pytesseract.image_to_string(image, lang='fra', config='--psm 4')
        return text if text.strip() else "Aucun texte détecté."
    except Exception as e:
        logging.error(f"Erreur OCR: {e}")
        return f"Erreur OCR: {str(e)}"

def extract_name_from_text(text: str) -> str:
    """Tente de détecter le nom complet depuis les premières lignes du texte."""
    if nlp:
        doc = nlp(text[:500])
        for ent in doc.ents:
            if ent.label_ == "PER" and len(ent.text.split()) >= 2:
                return ent.text.strip()
    # Fallback : première ligne non vide
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 3 and len(line) < 60 and not any(c in line for c in ['@', '/', '.']):
            return line
    return ""

def extract_email_from_text(text: str) -> str:
    """Extrait l'adresse email depuis le texte."""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ""

def extract_entities(text: str) -> dict:
    """Extrait compétences, entités NLP, email, nom depuis le texte brut."""
    entities = []
    if nlp:
        doc = nlp(text[:3000])
        for ent in doc.ents:
            if ent.label_ in ["PER", "ORG", "LOC"]:
                entities.append({"text": ent.text, "label": ent.label_})

    found_skills = list({kw for kw in SKILL_KEYWORDS if kw.lower() in text.lower()})

    preview = text.strip()[:1500]
    if len(text.strip()) > 1500:
        preview += "..."

    return {
        "raw_text": preview,
        "extracted_entities": entities,
        "skills": found_skills,
        "candidate_name": extract_name_from_text(text),
        "candidate_email": extract_email_from_text(text),
    }

def analyze_cv_file(file_content: bytes, filename: str) -> dict:
    """Point d'entrée principal : route le fichier vers OCR image ou extraction PDF."""
    filename_lower = filename.lower()
    text = ""

    if filename_lower.endswith('.pdf'):
        text = extract_text_from_pdf(file_content)
        # Si le PDF est scanné (image dans PDF), on tente un fallback OCR limité
        if not text.strip() or text.startswith("Erreur"):
            logging.warning("PDF texte vide, tentative OCR page 1...")
            text = "PDF scanné (OCR non disponible sans Poppler). " \
                   "Conseil : convertissez votre PDF en PNG pour un meilleur résultat."
    elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        text = extract_text_from_image(file_content)
    else:
        text = "Format de fichier non supporté."

    return extract_entities(text)
