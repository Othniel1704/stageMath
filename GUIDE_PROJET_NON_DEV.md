# StageMatch - Guide complet pour une personne non technique

Ce document a ete ecrit pour transmettre le projet a quelqu'un qui n'est pas developpeur.

L'objectif est simple :

- comprendre a quoi sert StageMatch
- savoir ce que l'application permet de faire
- savoir comment l'utiliser au quotidien
- savoir comment la lancer localement si besoin
- savoir quoi verifier en cas de probleme

## 1. C'est quoi StageMatch ?

StageMatch est une application qui aide un candidat a trouver des offres de stage ou d'alternance plus rapidement.

Le principe :

1. le candidat cree un compte
2. il depose son CV
3. l'application lit le CV automatiquement
4. elle identifie les competences, le profil et certains elements utiles
5. elle propose des offres pertinentes
6. le candidat peut enregistrer des offres pour plus tard
7. il peut suivre ce qu'il a deja postule ou non

En resume :

StageMatch sert a transformer un CV en recommandations d'offres, puis a aider la personne a organiser ses candidatures.

## 2. Ce que l'application fait aujourd'hui

### Espace candidat

L'utilisateur peut :

- creer un compte
- se connecter
- deposer un CV PDF ou image
- voir les competences detectees
- modifier son profil
- obtenir des matchs d'offres
- parcourir tout le catalogue d'offres
- sauvegarder une offre pour plus tard
- marquer une offre comme deja postulee
- suivre ses candidatures dans un espace dedie

### Cote intelligence / logique

L'application :

- lit le texte du CV
- extrait certaines competences techniques
- cree un profil candidat
- compare ce profil aux offres
- affiche un score de matching
- explique en partie pourquoi une offre remonte

### Cote suivi

L'application propose maintenant un petit systeme de suivi avec deux etats principaux :

- `A postuler plus tard`
- `Postulee`

Cela permet a l'utilisateur de ne pas perdre les offres interessantes.

## 3. Parcours utilisateur tres simple

Pour comprendre l'application, il faut retenir 4 ecrans principaux :

### 1. Upload du CV

Le candidat depose son CV.

Le systeme :

- lit le fichier
- extrait le nom, l'email, les competences
- enregistre le profil

### 2. Mes matchs

Le candidat voit les offres recommandees selon son profil.

Il peut :

- lire les offres
- ouvrir l'annonce originale
- garder une offre pour plus tard
- la marquer comme postulee

### 3. Catalogue

Le candidat voit toutes les offres disponibles, meme si elles ne sont pas forcement dans ses meilleurs matchs.

### 4. Suivi candidatures

Le candidat retrouve :

- les offres qu'il veut traiter plus tard
- les offres deja postulees

## 4. Comment lancer le projet localement

Cette partie est utile si la personne qui reprend le projet doit le faire tourner sur son ordinateur.

Le projet est separe en 2 parties :

- `backend` = la partie serveur / API
- `frontend` = la partie interface visible dans le navigateur

### Ce qu'il faut avoir sur l'ordinateur

Idealement :

- Python installe
- Node.js installe
- acces au projet Supabase
- les fichiers `.env` deja renseignes

### Lancer le backend

Ouvrir un terminal dans :

`backend/backend`

Puis lancer :

```powershell
.\\venv\\Scripts\\activate
uvicorn main:app --reload
```

Si tout va bien, le backend demarre en local sur :

[http://localhost:8000](http://localhost:8000)

La documentation technique de l'API devient visible ici :

[http://localhost:8000/docs](http://localhost:8000/docs)

### Lancer le frontend

Ouvrir un autre terminal dans :

`frontend`

Puis lancer :

```powershell
npm install
npm run dev
```

Si tout va bien, l'interface est visible ici :

[http://localhost:3000](http://localhost:3000)

## 5. Comment utiliser StageMatch en pratique

### Etape 1. Se connecter

Ouvrir l'application dans le navigateur et se connecter avec un compte utilisateur.

### Etape 2. Uploader un CV

Aller sur la page d'upload puis deposer un CV.

A verifier apres upload :

- le nom detecte semble correct
- l'email detecte semble correct
- les competences detectees semblent logiques

### Etape 3. Verifier le profil

Sur la page profil, on peut ajuster :

- le nom
- la localisation
- le type de contrat recherche
- les competences

Cette etape est importante car elle influence directement le matching.

### Etape 4. Consulter les matchs

Sur la page `Mes matchs`, l'utilisateur voit :

- les offres les plus proches de son profil
- un score
- une explication du score
- des competences liees a l'offre

### Etape 5. Enregistrer une offre pour plus tard

Depuis `Mes matchs` ou `Catalogue`, cliquer sur :

- `Garder pour plus tard`

L'offre est ensuite rangee dans `Suivi candidatures`.

### Etape 6. Marquer une offre comme postulee

Quand le candidat a vraiment postule :

- soit il le marque directement depuis la carte offre
- soit il le fait depuis `Suivi candidatures`

## 6. Ce qu'il faut savoir sur les scores

Le score de matching n'est pas une garantie.

C'est une aide a la priorisation.

Le score prend surtout en compte :

- la proximite entre le CV et l'offre
- les competences retrouvees
- la localisation
- le type de contrat

Une offre avec un score moyen peut quand meme etre interessante.

Il faut voir le score comme :

- une indication
- pas comme une verite absolue

## 7. Ou sont les donnees importantes

### Base de donnees

Le projet s'appuie sur Supabase.

Les tables importantes sont :

- `profiles`
  contient les informations du candidat et les competences extraites

- `job_offers`
  contient les offres

- `saved_jobs`
  contient les offres enregistrees et suivies

### Fichiers importants du projet

- [main.py](/stagemacth/backend/backend/main.py)
  point d'entree du backend

- [upload.py](/stagemacth/backend/backend/routers/upload.py)
  gestion de l'upload du CV

- [match.py](/stagemacth/backend/backend/routers/match.py)
  logique de matching

- [applications.py](/stagemacth/backend/backend/routers/applications.py)
  suivi des offres enregistrees et postulees

- [matches/page.tsx](/stagemacth/frontend/src/app/dashboard/matches/page.tsx)
  page principale pour consulter les offres

- [tracking/page.tsx](/stagemacth/frontend/src/app/dashboard/tracking/page.tsx)
  page de suivi des candidatures

## 8. Cas d'usage simple a expliquer a quelqu'un

Si vous devez presenter le projet a une personne non technique, vous pouvez dire :

"StageMatch aide un candidat a transformer son CV en opportunites concretes. Le CV est lu automatiquement, les offres les plus pertinentes ressortent, puis le candidat peut organiser ses candidatures avec un petit outil de suivi."

## 9. Les problemes les plus frequents

### 1. Le CV est upload mais aucun match ne ressort

Ca peut venir de :

- competences mal detectees
- profil non sauvegarde
- offre pas suffisamment proche
- parametres de localisation / contrat trop stricts

A verifier :

- page profil
- competences detectees
- page catalogue
- backend actif

### 2. Une offre ne peut pas etre enregistree

Ca peut venir de :

- backend non redemarre
- incoherence de statuts dans `saved_jobs`
- probleme de base Supabase

Le correctif recent a harmonise les statuts du suivi.

### 3. Le frontend s'ouvre mais pas les donnees

Souvent cela veut dire :

- le backend n'est pas lance
- l'URL de l'API dans les variables d'environnement n'est pas bonne
- Supabase ne repond pas

### 4. Le CV est analyse bizarrement

Cela arrive surtout si :

- le PDF est mal structure
- le texte n'est pas lisible
- le document est trop image / scan

Dans ce cas, il faut essayer un autre CV test ou un PDF plus propre.

## 10. Comment verifier rapidement que tout marche

Voici un test simple en 5 minutes :

1. lancer backend + frontend
2. se connecter
3. uploader un CV
4. verifier que des competences apparaissent
5. ouvrir `Mes matchs`
6. enregistrer une offre
7. aller dans `Suivi candidatures`
8. verifier que l'offre y apparait
9. la marquer comme postulee

Si ces 9 etapes fonctionnent, le coeur du produit fonctionne.

## 11. Ce qui a ete ameliore recemment

Les dernieres ameliorations importantes du projet sont :

- meilleur moteur de matching
- affichage des offres plus clair
- explication du score de matching
- meilleur fallback quand les embeddings ne sont pas disponibles
- systeme de suivi des candidatures plus lisible
- possibilite d'enregistrer une offre pour plus tard
- correction des statuts de suivi entre backend et base de donnees

## 12. Limites actuelles du projet

Le projet fonctionne, mais il faut connaitre ses limites :

- le matching reste une aide, pas une garantie
- la qualite depend beaucoup du CV source
- certaines offres peuvent manquer de competences structurees
- si les modeles d'IA ne sont pas disponibles localement, le systeme passe sur des heuristiques plus simples
- le suivi est encore volontairement simple

## 13. Evolutions naturelles possibles

Si quelqu'un reprend le projet plus tard, les evolutions logiques seraient :

- ajouter plus de statuts dans le suivi
  exemple : `Entretien`, `Refuse`, `Offre`

- permettre des notes par offre

- ajouter une vraie page admin de supervision

- ameliorer encore l'analyse du CV

- mieux expliquer pourquoi une offre est recommandee

- proposer des relances ou rappels

## 14. Resume ultra simple

StageMatch est une application de matching CV -> offres de stage / alternance.

Le candidat :

- depose son CV
- voit des offres pertinentes
- sauvegarde les offres interessantes
- suit ce qu'il a deja postule

Le systeme est deja utilisable, et les briques essentielles sont en place.
