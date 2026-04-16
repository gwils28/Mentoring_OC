# Pipeline CI/CD (livrable 4)

[![DSML P12 — agrireco](https://github.com/gwils28/Mentoring_OC/actions/workflows/dsml-p12-agrireco.yml/badge.svg)](https://github.com/gwils28/Mentoring_OC/actions/workflows/dsml-p12-agrireco.yml)

Fichier : [`.github/workflows/dsml-p12-agrireco.yml`](../../../.github/workflows/dsml-p12-agrireco.yml), à la racine du
dépôt, parce que GitHub Actions ne lit les workflows que dans ce dossier. Le dépôt contient plusieurs projets : le
filtre `paths:` ne déclenche ce workflow que si un fichier de ce projet (ou le workflow lui-même) change.

## Ce que fait le pipeline

```text
 push / pull request sur le dossier P12
                │
                ▼
 ┌──────────────────────────── job « qualite » ────────────────────────────┐
 │ uv sync --locked → ruff (lint + format) → requirements.txt = uv.lock ?  │
 │ → pytest (tests unitaires + tests de l'API avec le modèle versionné)    │
 └─────────────────────────────────┬───────────────────────────────────────┘
                                   │ seulement si tout est vert
                                   ▼
 ┌──────────────────────────── job « image » ──────────────────────────────┐
 │ docker build → conteneur lancé → test d'intégration :                   │
 │   /health répond, /predict > 0, /recommend renvoie 10 cultures,         │
 │   culture inconnue → 422                                                │
 │ → sur main uniquement : push ghcr.io/<propriétaire>/agrireco-api        │
 │   (tags : 7 premiers caractères du commit, et latest)                   │
 └─────────────────────────────────┬───────────────────────────────────────┘
                                   │ si un des deux jobs échoue
                                   ▼
          job « alerte » : résumé ❌ dans l'onglet Actions (+ e-mail GitHub)
```

| Étape | Pourquoi |
|---|---|
| `uv sync --locked` | Installe **exactement** les versions de `uv.lock` ; échoue si le lock ne correspond plus à `pyproject.toml` |
| `ruff check` / `ruff format --check` | Code lisible et homogène ; une erreur bloque la suite |
| Contrôle des `requirements.txt` | L'image Docker installe `api/requirements.txt` : on vérifie qu'il correspond toujours à `uv.lock` (sinon l'image n'aurait pas les mêmes versions que les tests) |
| `pytest` | Tests unitaires : fusion des données, métriques, sélection, recommandation, domaine de validité, configuration, API (`TestClient`), interface sans ML |
| Test d'intégration du conteneur | Vérifie l'image réellement construite, pas seulement le code : dépendances, modèle embarqué, démarrage |
| Publication GHCR | Registre d'images de GitHub, authentifié par le `GITHUB_TOKEN` fourni au job : aucun secret à créer |

## Déclencheurs

- `push` sur `main` qui touche le dossier du projet → tout le pipeline, **publication comprise** ;
- `pull_request` → qualité + image + test d'intégration, **sans publication** (une PR ne doit pas pousser d'image) ;
- `workflow_dispatch` → lancement manuel depuis l'onglet Actions.

`concurrency` annule un run de PR devenu inutile quand on pousse un nouveau commit ; sur `main`, les runs s'enchaînent
sans s'annuler (une publication en cours n'est jamais coupée).

## Que se passe-t-il en cas d'échec ?

- Chaque commande qui échoue rend le job **rouge** et arrête les étapes suivantes : si un test casse, l'image n'est
  ni construite ni publiée (`needs: qualite`). Le dernier code publié reste celui de `latest`.
- Le rapport de tests (`rapport-tests.xml`) est conservé en artefact même en cas d'échec (`if: always()`).
- Si le conteneur ne démarre pas, ses journaux sont affichés (`docker logs`).
- Le job `alerte` écrit un résumé lisible dans l'onglet Actions ; GitHub envoie aussi un **e-mail** à l'auteur du
  commit (réglage par défaut des notifications). Pour prévenir une équipe, on ajouterait une étape Slack ou Teams
  dans ce job (voir `ALLER_PLUS_LOIN.md`).
- Échecs simulés en local avec les mêmes commandes que le workflow : test volontairement faux (`pytest` en échec,
  donc job `qualite` rouge et job `image` sauté), conteneur lancé sans modèle (refus de démarrer : « Modèle
  introuvable »), `requirements.txt` modifié à la main (régénération puis `git diff --exit-code` en échec). Le premier essai réel du conteneur a
  d'ailleurs échoué : le modèle picklé dépendait de pyarrow, absent de l'image ; un test le vérifie désormais.

## Secrets

Aucun secret dans les fichiers. La publication utilise le `GITHUB_TOKEN` éphémère du run, avec des permissions
**minimales** : `contents: read` partout, `packages: write` seulement pour le job `image`.

## Utiliser l'image publiée

```bash
docker run -p 8000:8000 ghcr.io/gwils28/agrireco-api:latest
# puis http://localhost:8000/docs
```

Un paquet GHCR est **privé** à sa création : pour le rendre accessible sans authentification, le passer en public
dans *Packages → agrireco-api → Package settings*.

## Déploiement de l'interface (documenté, non réalisé)

Streamlit Community Cloud déploie `app/app.py` depuis le dépôt GitHub (fichier `app/requirements.txt`). L'interface a
besoin d'une API **joignable sur Internet** : il faut d'abord héberger l'image (Cloud Run, Render, Azure Container
Apps…) puis renseigner son adresse dans le secret `API_URL` de l'application Streamlit. En local, tout tient dans
`docker compose up --build`.

## Ce que ce pipeline ne fait pas (et pourquoi)

Il ne **réentraîne pas** le modèle : les données brutes (36 Mo) ne sont pas dans le dépôt et l'entraînement est un
choix humain (on relit les résultats avant de servir un modèle). Le modèle versionné `models/model.joblib` est produit
par `uv run agrireco all` sur le poste du data scientist, puis committé : la CI teste et emballe ce modèle-là.
Automatiser le réentraînement (déclenché par de nouvelles données, avec validation avant mise en service) est la
suite logique, décrite dans `ALLER_PLUS_LOIN.md`.
