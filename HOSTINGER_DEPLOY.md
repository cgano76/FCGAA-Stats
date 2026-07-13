# Deploiement Hostinger - FCGAA Stats

## Option recommandee : Hostinger Node.js Web App

Cette option conserve les fonctions serveur de la maquette :

- import PDF/TXT via API locale ;
- extraction via scripts Python si Python et les dependances sont disponibles ;
- sauvegarde d'etat dans `storage/interface-state.json` ;
- appel OpenAI cote serveur avec `OPENAI_API_KEY`.

### Preparation

1. Pousser le projet sur GitHub.
2. Verifier que ces fichiers sont presents a la racine :
   - `package.json`
   - `serve-interface.mjs`
   - `index.html`
   - `interface-fcgaa-stats.html`
3. Ne jamais envoyer `.env`, `.env.local`, `storage/`, `node_modules/` ou les fichiers importes.

### Configuration Hostinger

Dans hPanel Hostinger :

1. Aller dans `Websites`.
2. Choisir le site ou domaine.
3. Creer une application `Node.js Web App`.
4. Connecter le depot GitHub ou uploader le ZIP genere.
5. Parametrer :
   - Build command : `npm install`
   - Start command : `npm start`
   - Node version : 22 si disponible
6. Ajouter les variables d'environnement :
   - `APP_ENV=production`
   - `OPENAI_API_KEY=...` uniquement si l'analyse IA doit appeler OpenAI
   - `OPENAI_TEXT_MODEL=gpt-4.1-mini`

L'application doit ensuite etre accessible a la racine du domaine, par exemple :

```text
https://votre-domaine.fr/
```

La racine redirige vers :

```text
https://votre-domaine.fr/interface-fcgaa-stats.html
```

## Option alternative : upload HTML dans public_html

Cette option est utile pour une demonstration statique.

1. Uploader dans `public_html` :
   - `index.html`
   - `interface-fcgaa-stats.html`
   - le dossier `frontend/`
2. Ouvrir le domaine.

Limites de l'option statique :

- pas d'extraction PDF/TXT cote serveur ;
- pas d'appel OpenAI securise ;
- pas de sauvegarde serveur ;
- pas d'acces aux fichiers locaux `S:/...` ou `J:/...`.

## Creer un ZIP propre pour Hostinger

Depuis PowerShell :

```powershell
cd "C:\Users\CONSEIL\Documents\FCGAA SAAS"
.\scripts\prepare_hostinger_zip.ps1
```

Archive generee :

```text
dist-hostinger/fcgaa-stats-hostinger.zip
```

Cette archive exclut les donnees locales sensibles et les fichiers temporaires.

## Points a verifier apres mise en ligne

- La page `/interface-fcgaa-stats.html` s'ouvre.
- Les menus s'affichent correctement.
- Les imports fonctionnent si l'hebergement Node autorise l'execution Python.
- L'analyse IA affiche une erreur claire si `OPENAI_API_KEY` n'est pas configuree.
- Les chemins reseau Windows `S:/...` et `J:/...` ne sont pas disponibles en ligne : les fichiers devront etre uploades ou stockes sur un espace accessible au serveur.
