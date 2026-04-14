-- ============================================================
-- StageMatch - Migration v5 : nettoyage des statuts saved_jobs
-- Harmonise les anciennes valeurs anglaises avec le format Antigravity
-- ============================================================

BEGIN;

-- 1. Supprimer temporairement l'ancienne contrainte si elle existe
ALTER TABLE public.saved_jobs
DROP CONSTRAINT IF EXISTS check_status;

-- 2. Normaliser les anciennes valeurs vers le format français
UPDATE public.saved_jobs
SET status = 'Enregistré'
WHERE status IN ('saved', 'Enregistre', 'Enregistré');

UPDATE public.saved_jobs
SET status = 'Postulé'
WHERE status IN ('applied', 'Postule', 'Postulé');

UPDATE public.saved_jobs
SET status = 'Entretien'
WHERE status IN ('interview', 'Entretien');

UPDATE public.saved_jobs
SET status = 'Offre'
WHERE status IN ('offer', 'Offre');

UPDATE public.saved_jobs
SET status = 'Refusé'
WHERE status IN ('rejected', 'Refuse', 'Refusé');

-- 3. Définir une valeur par défaut cohérente
ALTER TABLE public.saved_jobs
ALTER COLUMN status SET DEFAULT 'Enregistré';

-- 4. Recréer la contrainte avec les valeurs finales autorisées
ALTER TABLE public.saved_jobs
ADD CONSTRAINT check_status
CHECK (status IN ('Enregistré', 'Postulé', 'Entretien', 'Offre', 'Refusé'));

COMMIT;
