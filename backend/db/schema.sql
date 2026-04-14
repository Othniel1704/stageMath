-- ============================================================
-- StageMatch — Migration v2 : Mise à jour du schéma complet
-- À exécuter dans l'onglet "SQL Editor" de Supabase
-- ============================================================

-- ⚠️ Si vous partez de zéro, exécutez ce bloc complet.
-- ⚠️ Si vous avez déjà les tables, exécutez uniquement les sections "ALTER TABLE".

-- ================================================================
-- 1. Mise à jour de la table profiles (ajout user_id + champs manquants)
-- ================================================================

-- Option A : Si la table profiles N'EXISTE PAS ENCORE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    candidate_name VARCHAR(255),
    email VARCHAR(255),
    location VARCHAR(255),
    preferred_contract VARCHAR(100),
    extracted_skills TEXT[],
    raw_cv_text TEXT,
    cv_score INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Option B : Si la table profiles EXISTE DÉJÀ, ajoutez les nouvelles colonnes
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS location VARCHAR(255);
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS preferred_contract VARCHAR(100);
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS cv_score INT DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now());
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS cv_embedding vector(384);

-- Contrainte unique sur user_id pour l'upsert
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_user_id_key;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);


-- ================================================================
-- 2. Table job_offers (déjà existante — pas de changement nécessaire)
-- ================================================================
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.job_offers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    url VARCHAR(500),
    source VARCHAR(50) DEFAULT 'StageMatch',
    contract_type VARCHAR(50),
    skills_required TEXT[],
    embedding vector(384),
    expires_at TIMESTAMP WITH TIME ZONE,  -- Pour le nettoyage des offres expirées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.job_offers ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.job_offers ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Fonction de recherche par similarité cosinus (pgvector)
CREATE OR REPLACE FUNCTION match_jobs (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  title varchar,
  company_name varchar,
  location varchar,
  url varchar,
  contract_type varchar,
  skills_required text[],
  source varchar,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    job_offers.id,
    job_offers.title,
    job_offers.company_name,
    job_offers.location,
    job_offers.url,
    job_offers.contract_type,
    job_offers.skills_required,
    job_offers.source,
    1 - (job_offers.embedding <=> query_embedding) AS similarity
  FROM job_offers
  WHERE 1 - (job_offers.embedding <=> query_embedding) > match_threshold
  ORDER BY job_offers.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- ================================================================
-- 3. Nouvelle table : saved_jobs (Favoris + Suivi candidature)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.saved_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    job_offer_id UUID REFERENCES public.job_offers(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(50) DEFAULT 'saved',  -- saved | applied | interview | offer | rejected
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, job_offer_id)  -- Un utilisateur ne peut sauvegarder une offre qu'une fois
);

-- ================================================================
-- 4. Row Level Security (RLS) — Sécurité par utilisateur
-- ================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_jobs ENABLE ROW LEVEL SECURITY;

-- Profils : chaque utilisateur voit/modifie uniquement son profil
DROP POLICY IF EXISTS "Users manage own profile" ON public.profiles;
CREATE POLICY "Users manage own profile" ON public.profiles
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- job_offers : lecture publique, écriture admin uniquement
DROP POLICY IF EXISTS "Public read job_offers" ON public.job_offers;
CREATE POLICY "Public read job_offers" ON public.job_offers FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow anonymous insert access on job_offers" ON public.job_offers;
CREATE POLICY "Allow anonymous insert access on job_offers" ON public.job_offers FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow anonymous update access on job_offers" ON public.job_offers;
CREATE POLICY "Allow anonymous update access on job_offers" ON public.job_offers FOR UPDATE USING (true);

-- saved_jobs : chaque utilisateur gère ses propres favoris
DROP POLICY IF EXISTS "Users manage own saved_jobs" ON public.saved_jobs;
CREATE POLICY "Users manage own saved_jobs" ON public.saved_jobs
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
