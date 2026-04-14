# Migration v5 - Nettoyage des statuts `saved_jobs`

Ce document explique comment lancer la migration SQL `migration_v5_saved_jobs_status_cleanup.sql`, a quoi elle sert, et comment verifier qu'elle a bien fonctionne.

## Pourquoi cette migration existe

Le projet a eu deux formats de statuts pour la table `public.saved_jobs` :

- ancien format : `saved`, `applied`, `interview`, `offer`, `rejected`
- nouveau format Antigravity : `Enregistré`, `Postulé`, `Entretien`, `Offre`, `Refusé`

Le backend a ete corrige pour etre compatible avec les deux formats, mais si la base contient encore un melange de valeurs, cela peut provoquer des erreurs lors de l'enregistrement d'une offre.

La migration v5 sert a :

1. convertir toutes les anciennes valeurs vers le format final Antigravity
2. remettre une valeur par defaut propre sur la colonne `status`
3. recreer une contrainte SQL coherente sur les statuts autorises

## Fichier a executer

Le script SQL est ici :

[migration_v5_saved_jobs_status_cleanup.sql](/C:/Users/Cedric%20Adannou/Desktop/stagemacth/backend/backend/db/migration_v5_saved_jobs_status_cleanup.sql)

## Comment la lancer dans Supabase

1. Ouvrez votre projet Supabase.
2. Allez dans `SQL Editor`.
3. Creez une nouvelle requete.
4. Ouvrez le contenu du fichier `migration_v5_saved_jobs_status_cleanup.sql`.
5. Copiez-collez tout le script dans l'editeur SQL.
6. Cliquez sur `Run`.

## Ce que fait la migration

Le script execute les operations suivantes :

1. supprime temporairement la contrainte `check_status` si elle existe
2. remplace :
   `saved` -> `Enregistré`
   `applied` -> `Postulé`
   `interview` -> `Entretien`
   `offer` -> `Offre`
   `rejected` -> `Refusé`
3. remet la valeur par defaut de `status` a `Enregistré`
4. recree la contrainte `check_status` avec les seules valeurs autorisees :
   `Enregistré`, `Postulé`, `Entretien`, `Offre`, `Refusé`

Le tout est execute dans une transaction SQL (`BEGIN ... COMMIT`) pour eviter un etat partiellement migre.

## Comment verifier que ca a marche

Apres execution, vous pouvez lancer ces requetes dans Supabase SQL Editor.

### 1. Voir les statuts encore presents

```sql
SELECT status, COUNT(*)
FROM public.saved_jobs
GROUP BY status
ORDER BY status;
```

Resultat attendu :

- plus aucune ligne avec `saved`
- plus aucune ligne avec `applied`
- uniquement des valeurs du type `Enregistré`, `Postulé`, `Entretien`, `Offre`, `Refusé`

### 2. Verifier la valeur par defaut

```sql
SELECT column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'saved_jobs'
  AND column_name = 'status';
```

Resultat attendu :

- une valeur par defaut basee sur `Enregistré`

### 3. Verifier qu'une offre peut etre sauvegardee

Depuis l'application :

1. ouvrez `Mes matchs` ou `Catalogue`
2. cliquez sur `Garder pour plus tard`
3. allez dans `Suivi candidatures`
4. verifiez que l'offre apparait bien dans `A postuler plus tard`

## Comment le backend fonctionne maintenant

Le backend a ete mis a jour dans :

[applications.py](/C:/Users/Cedric%20Adannou/Desktop/stagemacth/backend/backend/routers/applications.py)

Le comportement actuel est :

- en base, on ecrit les statuts au format Antigravity : `Enregistré`, `Postulé`
- vers le frontend, on renvoie des statuts normalises : `saved`, `applied`
- si d'anciennes lignes existent encore, le backend sait les lire et les convertir logiquement

Donc :

- la base reste coherente
- le frontend reste simple
- le systeme de suivi continue de fonctionner sans casser l'existant

## En cas d'erreur

Si la migration echoue :

1. copiez le message d'erreur de Supabase SQL Editor
2. verifiez si une contrainte `check_status` existe deja avec un autre nom
3. verifiez si la table `public.saved_jobs` existe bien

Requetes utiles :

```sql
SELECT conname
FROM pg_constraint
WHERE conrelid = 'public.saved_jobs'::regclass;
```

```sql
SELECT *
FROM public.saved_jobs
LIMIT 10;
```

## Resume

Lancer cette migration permet d'aligner definitivement la table `saved_jobs` avec la logique actuelle du backend et du suivi des candidatures.
