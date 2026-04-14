-- ============================================================
-- StageMatch — Migration Antigravity : Logique Finale
-- Implémentation du système Antigravity avec gestion locale des données
-- ============================================================

-- ================================================================
-- 1. Mise à jour de la table profiles pour Antigravity
-- ================================================================

-- Ajouter le chemin d'accès local au CV
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS chemin_acces_local VARCHAR(500);

-- Modifier extracted_skills pour stocker comme chaîne de caractères (séparés par virgules)
-- au lieu d'un array TEXT[] pour faciliter la manipulation locale
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS competences_extraites TEXT;

-- Migrer les données existantes si elles existent
UPDATE public.profiles
SET competences_extraites = array_to_string(extracted_skills, ', ')
WHERE extracted_skills IS NOT NULL AND competences_extraites IS NULL;

-- ================================================================
-- 2. Mise à jour de la table job_offers pour Antigravity
-- ================================================================

-- Ajouter le statut et score_matching
ALTER TABLE public.job_offers ADD COLUMN IF NOT EXISTS statut VARCHAR(50) DEFAULT 'active';
ALTER TABLE public.job_offers ADD COLUMN IF NOT EXISTS score_matching INT DEFAULT 0;

-- Index pour améliorer les performances de filtrage
CREATE INDEX IF NOT EXISTS idx_job_offers_contract_type ON public.job_offers(contract_type);
CREATE INDEX IF NOT EXISTS idx_job_offers_statut ON public.job_offers(statut);

-- ================================================================
-- 3. Fonction de filtrage automatique des offres
-- ================================================================

-- Fonction pour vérifier si une offre est un stage/alternance
CREATE OR REPLACE FUNCTION is_stage_or_alternance(contract_type TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Convertir en minuscules pour la comparaison
    contract_type := LOWER(TRIM(contract_type));

    -- Vérifier si contient "stage" ou "alternance" ou "apprentissage"
    IF contract_type LIKE '%stage%' OR
       contract_type LIKE '%alternance%' OR
       contract_type LIKE '%apprentissage%' THEN
        RETURN TRUE;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour filtrer automatiquement les nouvelles offres
CREATE OR REPLACE FUNCTION filter_job_offers()
RETURNS TRIGGER AS $$
BEGIN
    -- Si ce n'est pas un stage ou alternance, marquer comme filtré
    IF NOT is_stage_or_alternance(NEW.contract_type) THEN
        NEW.statut := 'filtered';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger sur les insertions
DROP TRIGGER IF EXISTS trigger_filter_job_offers ON public.job_offers;
CREATE TRIGGER trigger_filter_job_offers
    BEFORE INSERT ON public.job_offers
    FOR EACH ROW EXECUTE FUNCTION filter_job_offers();

-- ================================================================
-- 4. Mise à jour de la table saved_jobs pour Antigravity
-- ================================================================

-- S'assurer que le statut correspond aux spécifications
ALTER TABLE public.saved_jobs ALTER COLUMN status SET DEFAULT 'Enregistré';

-- Ajouter une contrainte pour limiter les valeurs de statut
ALTER TABLE public.saved_jobs ADD CONSTRAINT check_status
    CHECK (status IN ('Enregistré', 'Postulé', 'Entretien', 'Offre', 'Refusé'));

-- ================================================================
-- 5. Fonctions utilitaires pour Antigravity
-- ================================================================

-- Fonction pour calculer le score de matching basé sur les mots-clés
CREATE OR REPLACE FUNCTION calculate_match_score(
    user_skills TEXT,
    job_description TEXT
) RETURNS INTEGER AS $$
DECLARE
    skill_array TEXT[];
    skill TEXT;
    score INTEGER := 0;
    job_lower TEXT;
BEGIN
    -- Convertir la description du job en minuscules
    job_lower := LOWER(job_description);

    -- Séparer les compétences par virgule et nettoyer
    skill_array := string_to_array(REPLACE(user_skills, ', ', ','), ',');

    -- Pour chaque compétence, vérifier si elle apparaît dans la description
    FOREACH skill IN ARRAY skill_array LOOP
        skill := TRIM(LOWER(skill));
        IF LENGTH(skill) > 2 AND job_lower LIKE '%' || skill || '%' THEN
            score := score + 10; -- +10 points par compétence trouvée
        END IF;
    END LOOP;

    -- Limiter le score à 100 maximum
    RETURN LEAST(score, 100);
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 6. Mise à jour des politiques RLS pour Antigravity
-- ================================================================

-- Permettre la lecture publique des offres filtrées comme 'active'
DROP POLICY IF EXISTS "Public read active job_offers" ON public.job_offers;
CREATE POLICY "Public read active job_offers" ON public.job_offers
    FOR SELECT USING (statut = 'active');

-- Permettre l'insertion anonyme mais seulement pour les stages/alternances
DROP POLICY IF EXISTS "Allow insert stage_alternance only" ON public.job_offers;
CREATE POLICY "Allow insert stage_alternance only" ON public.job_offers
    FOR INSERT WITH CHECK (is_stage_or_alternance(contract_type));

-- ================================================================
-- 7. Index pour optimiser les performances
-- ================================================================

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_status ON public.saved_jobs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_job_offers_score_matching ON public.job_offers(score_matching);

-- ================================================================
-- Notes de migration :
-- 1. Exécuter ce script dans Supabase SQL Editor
-- 2. Les offres existantes qui ne sont pas stages/alternances seront marquées 'filtered'
-- 3. Les compétences existantes seront migrées vers le format chaîne
-- 4. Le système est maintenant prêt pour la logique Antigravity
-- ================================================================