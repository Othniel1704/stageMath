-- ============================================================
-- StageMatch — Migration v3 : Suivi des candidatures
-- ============================================================

-- Ajout d'une colonne pour la date de candidature exacte sur une offre
ALTER TABLE public.saved_jobs ADD COLUMN IF NOT EXISTS applied_at TIMESTAMP WITH TIME ZONE;
