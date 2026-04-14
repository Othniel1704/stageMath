import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

# Vérifier les offres dans la base
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])
result = supabase.table('job_offers').select('*').limit(10).execute()
print('Nombre total d offres:', len(result.data) if result.data else 0)

if result.data:
    print('Exemples d offres:')
    for i, offer in enumerate(result.data[:5]):
        title = offer.get('title', 'N/A')
        company = offer.get('company_name', 'N/A')
        location = offer.get('location', 'N/A')
        skills = offer.get('skills_required', [])
        print(f'{i+1}. {title} ({company}) - {location}')
        print(f'   Competences: {skills}')
        print(f'   Description preview: {offer.get("description", "")[:100]}...')
        print()
else:
    print('Aucune offre trouvee dans la base de donnees')

# Vérifier aussi les profils utilisateurs
print('\n--- PROFILS UTILISATEURS ---')
profiles = supabase.table('profiles').select('*').limit(5).execute()
print('Nombre de profils:', len(profiles.data) if profiles.data else 0)
if profiles.data:
    for profile in profiles.data:
        print(f'User ID: {profile.get("user_id", "N/A")}')
        print(f'Competences extraites: {profile.get("competences_extraites", "N/A")}')
        print(f'Raw CV text length: {len(profile.get("raw_cv_text", ""))}')
        print()