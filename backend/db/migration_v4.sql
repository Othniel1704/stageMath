-- ============================================================
-- StageMatch — Migration v4 : Colonnes manquantes pour Antigravity
-- ============================================================

-- Ajout des colonnes manquantes à la table profiles
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS competences_extraites TEXT;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS chemin_acces_local VARCHAR(500);

-- Ajout de updated_at à saved_jobs pour le suivi des modifications
ALTER TABLE public.saved_jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now());

-- Mettre à jour les enregistrements existants pour updated_at
UPDATE public.saved_jobs SET updated_at = created_at WHERE updated_at IS NULL;
