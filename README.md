# FCGAA Stats

Dossier de conception du SaaS professionnel FCGAA Stats.

Objectif : gerer, exploiter, analyser et publier les statistiques agricoles FCGAA a partir des recueils PDF fournis, avec validation humaine et tracabilite de chaque valeur.

Documents principaux :

- [Dossier de conception complet](docs/conception/DOSSIER_CONCEPTION_FCGAA_STATS.md)

## Lancement local

1. Optionnel : copier `.env.example` vers `.env` pour personnaliser la configuration.
2. Renseigner `OPENAI_API_KEY` dans `.env` ou `.env.local` si le module IA doit appeler OpenAI Platform.
3. Lancer l'environnement :

```powershell
docker compose up --build
```

URLs locales :

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs

## Interface HTML autonome

Pour ouvrir uniquement la maquette HTML avec rechargement automatique :

```powershell
node serve-interface.mjs
```

Puis ouvrir :

```text
http://127.0.0.1:5173/interface-fcgaa-stats.html
```

Si le port 5173 est occupe, le serveur prend automatiquement le port suivant et l'ecrit dans `.interface-server-port`.

Flux disponible dans cette interface locale :

- selection d'un ou plusieurs PDF ;
- envoi au serveur local `POST /api/import-pdf` ;
- extraction texte via `scripts/extract_pdf.py` et `pypdf` ;
- import du fichier TXT `STATISTIQUES_FCGAA.txt` avec decodage des colonnes depuis `EXPORTATION_DICTIONNAIRE.xlsx` ;
- utilisation possible du TXT pour comparer ou remplacer les donnees importees depuis les PDF ;
- liaison des fichiers Excel du repertoire `Rapports/XLSX` aux professions ;
- stockage local des imports et valeurs dans `storage/fcgaa-stats.sqlite` pour disposer d'une vraie base pendant le prototype local ;
- registre des imports PDF charges, avec actions verifier les doublons, remplacer et supprimer ;
- suppression automatique d'un ancien import lorsque le meme fichier produit une extraction strictement identique ;
- creation de cellules candidates dans l'ecran Validation, avec indicateur, colonne, valeur, unite, page, espace et source ;
- extraction de `Fragilite financiere` en plus des autres indicateurs detectes ;
- cloture et recolte portees par chaque valeur ; si la recolte n'est pas detectee, elle reprend la cloture ;
- lien PDF local par valeur, avec ancre de page ;
- filtres de validation par indicateur, colonne, espace, statut, cloture et recolte ;
- filtres de validation par profession et niveau de confiance ;
- liste d'indicateurs alimentee automatiquement par les donnees importees ;
- tableau de synthese de l'onglet Validation limite aux totaux : professions, exploitations, SAU, Produit Brut ;
- compteur de lignes selectionnees et validation de toutes les lignes selectionnees, meme si elles ne sont pas toutes visibles ;
- suppression des donnees a valider, par selection ou en masse ;
- liste separee des donnees deja validees ;
- affichage limite par defaut avec bouton pour afficher toutes les lignes ;
- entete de tableau de validation fixe pendant le defilement ;
- synthese apres import : zones, quartiles, indicateurs, professions ;
- selection de lignes, validation en masse et historique des validations ;
- bouton `Tout valider` sur toutes les valeurs statistiques en attente, independamment des filtres, de la cloture ou de la recolte ;
- onglet Professions recapitulant profession, type conventionnel/BIO, cloture, recolte, pages PDF associees et liens XLSX quand ils existent ;
- recherche rapide dans le tableau de bord, avec restitution des valeurs validees dans l'ordre des lignes et colonnes du PDF ;
- bouton `Reinitialiser` remettant a zero tous les filtres du tableau de bord ;
- exports PDF complet, Excel multi-onglets et CSV du tableau de bord ;
- exports PDF, CSV, XML ou JSON des donnees a verifier, sans accents, sans caracteres non ASCII et avec dedoublonnage ;
- comparaison des indicateurs valides avec analyse descriptive et infographie de synthese ;
- filtres IA par profession, cloture et recolte, avec appel OpenAI cote serveur si `OPENAI_API_KEY` est configuree ;
- masquage des menus Comparaisons, Professions, Analyses IA, Comparateur exploitant et Exports tant qu'aucune donnee statistique n'est importee ;
- ajout optionnel d'une source web explicite dans l'onglet Administration, reserve admin/super admin ; le contexte web reste cite separement et ne remplace pas les valeurs FCGAA ;
- persistance de l'etat de l'interface dans `storage/interface-state.json` pour conserver imports, validations, historiques, liens XLSX et sources apres rechargement ;
- comparateur exploitant pour importer un fichier FEC, balance ou liasse, extraire les comptes et les comparer aux references validees par profession, cloture, recolte et zone ;
- chatbot flottant local pour interroger les valeurs validees, les sources statistiques, les imports, les professions, les XLSX et les etapes de validation sans inventer de chiffre ni restituer d'information technique confidentielle ;
- index documentaire statistique du chatbot limite aux PDF statistiques, Dico Calculs, Dico Importation, TXT source et dictionnaire Excel, avec citations de sources dans les reponses ;
- validation ou rejet manuel dans l'interface.

Regles d'export :

- `type_valeur = valeur` n'utilise jamais l'unite `%` ;
- les pourcentages restent en `%` avec `type_valeur = pourcentage` ;
- les montants sont exportes en `K EUR` pour eviter les caracteres parasites dans les fichiers CSV/JSON ;
- les ratios, surfaces et UMO restent exportes avec leur unite propre.

Les valeurs extraites restent candidates : aucune donnee n'est consideree validee sans action humaine.

## Deploiement Hostinger

Le projet est prepare pour Hostinger en deux modes :

- `Node.js Web App` : mode recommande pour conserver les API locales, l'import et l'analyse IA cote serveur ;
- `public_html` statique : mode demonstration HTML uniquement, sans extraction PDF/TXT ni appel OpenAI securise.

Guide detaille :

- [HOSTINGER_DEPLOY.md](HOSTINGER_DEPLOY.md)

Creation d'une archive propre :

```powershell
.\scripts\prepare_hostinger_zip.ps1
```

## Structure

- `frontend/` : interface Next.js/React en francais.
- `backend/` : API FastAPI et modele de donnees.
- `infra/` : initialisation PostgreSQL.
- `docs/` : conception fonctionnelle et technique.

Statut actuel :

- Branche de travail : `codex/dossier-conception-fcgaa-stats`
- Livrable realise : conception fonctionnelle, technique et MVP
- Code applicatif : socle initial ajoute, sans chiffres fictifs et sans donnees validees importees
