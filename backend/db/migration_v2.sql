-- ============================================================
-- StageMatch — MIGRATION RAPIDE (copier-coller dans Supabase SQL Editor)
-- ============================================================

-- 1. Ajouter les colonnes manquantes à la table profiles
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS location VARCHAR(255);
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS preferred_contract VARCHAR(100);
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS cv_score INT DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 2. Contrainte unique sur user_id (nécessaire pour le upsert)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_user_id_key') THEN
    ALTER TABLE public.profiles ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);
  END IF;
END $$;

-- 3. Colonne expires_at pour job_offers (nettoyage)
ALTER TABLE public.job_offers ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;

-- 4. Table saved_jobs (favoris)
CREATE TABLE IF NOT EXISTS public.saved_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    job_offer_id UUID REFERENCES public.job_offers(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(50) DEFAULT 'saved',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, job_offer_id)
);

-- 5. RLS — politiques permissives pour les profils (lisibles et éditables par le propriétaire)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Supprimer les anciennes politiques si elles existent
DROP POLICY IF EXISTS "Allow anonymous read access on profiles" ON public.profiles;
DROP POLICY IF EXISTS "Allow anonymous insert access on profiles" ON public.profiles;
DROP POLICY IF EXISTS "Allow anonymous update access on profiles" ON public.profiles;
DROP POLICY IF EXISTS "Users manage own profile" ON public.profiles;
DROP POLICY IF EXISTS "profiles_select" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update" ON public.profiles;

-- Nouvelles politiques : un utilisateur ne voit/modifie que SON profil
CREATE POLICY "profiles_select" ON public.profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "profiles_insert" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "profiles_update" ON public.profiles
  FOR UPDATE USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 6. RLS saved_jobs
ALTER TABLE public.saved_jobs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users manage own saved_jobs" ON public.saved_jobs;
CREATE POLICY "saved_jobs_all" ON public.saved_jobs
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
