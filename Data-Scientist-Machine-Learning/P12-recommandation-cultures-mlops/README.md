# P12 — Concevez un système de recommandations pour une agriculture optimisée par les données

**Parcours Data Scientist Machine Learning · OpenClassrooms · optimiser un entraînement et automatiser son déploiement**

[![DSML P12 — agrireco](https://github.com/gwils28/Mentoring_OC/actions/workflows/dsml-p12-agrireco.yml/badge.svg)](https://github.com/gwils28/Mentoring_OC/actions/workflows/dsml-p12-agrireco.yml)

Agritech Answers veut une application qui **prédit** le rendement d'une culture à partir des conditions, et
**recommande** une culture en simulant toutes les cultures possibles. Le projet couvre toute la chaîne : données,
modèle optimisé et suivi dans MLflow, API FastAPI dans Docker, interface Streamlit, CI/CD GitHub Actions et rapport
métier.

## Par où commencer ?

| Vous êtes… | Ouvrez |
|---|---|
| **Mentor**, avant une séance | [kit-mentor/](kit-mentor/) : les pièges des données (jeu simulé, doublons, fusion impossible), chiffres de référence, déroulé, questions d'oral, erreurs fréquentes, grille, soutenance |
| **Apprenant**, en début de projet | la page interactive [site/index.html](site/index.html) (étapes, labos, quiz, check-list) : le mentor en partage le lien publié ; sur GitHub, le fichier s'affiche en code source |
| **Apprenant**, bloqué sur une notion | [pedagogie/](pedagogie/) : 9 fiches, une notion chacune, sur les vraies données |
| Curieux des pratiques actuelles | [ALLER_PLUS_LOIN.md](ALLER_PLUS_LOIN.md) (prix, données à la parcelle, registre de modèles, dérive, incertitude) |
| À la recherche de la référence | [notebooks/](notebooks/), [src/agrireco/](src/agrireco/), [api/](api/), [app/](app/), [docs/ci_cd.md](docs/ci_cd.md), [presentation/](presentation/) |

> Le corrigé sert au mentor à **comparer** ; on ne le transmet pas à l'apprenant avant sa soutenance (le dépôt est
> public). Ses fichiers ne suivent pas le nommage de dépôt OpenClassrooms (`Nom_Prenom_1_Screenshot_mmaaaa`…),
> réservé aux livrables de l'apprenant.

### Les 5 livrables OpenClassrooms dans le corrigé

| # | Livrable | Fichiers |
|---|---|---|
| 1 | Captures MLflow (.png) | [presentation/figures/mlflow_*.png](presentation/figures/) (5 captures, régénérées par [scripts/captures_mlflow.py](scripts/captures_mlflow.py)) + export [data/processed/mlflow_runs.csv](data/processed/mlflow_runs.csv) |
| 2 | Notebooks ou scripts d'entraînement | [notebooks/01_exploration_fusion.ipynb](notebooks/01_exploration_fusion.ipynb), [notebooks/02_modelisation_mlflow.ipynb](notebooks/02_modelisation_mlflow.ipynb), [src/agrireco/train.py](src/agrireco/train.py) |
| 3 | Pipeline MLOps | [src/agrireco/](src/agrireco/) (`prepare` → `train` → `evaluate`), [config.yaml](config.yaml), [api/Dockerfile](api/Dockerfile), [docker-compose.yml](docker-compose.yml) |
| 4 | Pipeline CI/CD (.yaml) | [.github/workflows/dsml-p12-agrireco.yml](../../.github/workflows/dsml-p12-agrireco.yml) + [docs/ci_cd.md](docs/ci_cd.md) |
| 5 | Rapport métier (.pdf) | [livrables/rapport_metier.pdf](livrables/rapport_metier.pdf), généré par [scripts/rapport_metier.py](scripts/rapport_metier.py) depuis `resultats.json` |

## Résultats du corrigé

| Étape | Résultat |
|---|---|
| Jeu « Agriculture Crop Yield » | **simulé** : 1 000 000 de lignes, les 6 cultures au même rendement moyen (4,65 t/ha), 231 rendements négatifs, ni pays ni année ; une droite explique 91,3 % du rendement (pluie, engrais, irrigation). ACP : 5 valeurs propres ≈ 1, aucune structure |
| Fusion | impossible avec le jeu simulé (seule clé commune : la culture, colonnes constantes). Fichiers FAO / Banque mondiale reconstruits : `yield_df.csv` avait 28 242 lignes pour 13 130 clés ; avec les noms de pays harmonisés, **15 794 lignes, 119 pays, 10 cultures, 1990-2013** |
| Validation | test sur **24 pays jamais vus** ; réglages en validation croisée groupée par pays. Une forêt par défaut fait 0,28 (RMSE du log) en validation aléatoire et 0,79 par pays, pire que la médiane de la culture (0,73) |
| Optimisation (MLflow) | 4 expériences, 78 runs ; référence 0,734 ; Ridge 0,641, forêt optimisée 0,634, boosting optimisé 0,638 ; hyperparamètre décisif `min_samples_leaf` ; **Ridge retenu** par la règle de parcimonie fixée à l'avance |
| Test final | **erreur relative médiane 37 %** (facteur typique 1,47) ; RMSE-log 0,608 (IC 95 % 0,53 – 0,68) contre 0,699 pour la référence et 0,680 avec la culture seule ; 0,51 à 0,67 sur 20 autres tirages de pays |
| Variables | la culture domine ; puis les pesticides (tonnes nationales : taille et équipement du pays, pas un effet du produit) et la température ; la pluie (une valeur par pays) n'apporte presque rien |
| Recommandation | bonne 1ʳᵉ place 37,5 %, contre **39,6 % pour un classement fixe** des cultures et 17,2 % au hasard ; écart −2,1 points (IC −10 à +7,5) : **le modèle ne recommande pas mieux qu'une liste fixe** (règle de décision fixée avant les résultats) |
| Industrialisation | API (`/predict`, `/recommend`, `/health`, domaine de validité signalé), image Docker testée en conteneur dans la CI, publication GHCR, interface Streamlit sans ML |

Constat principal : la **prédiction** est utilisable comme ordre de grandeur du rendement **moyen national**, pas à
la parcelle ; la **recommandation** ne fait pas mieux qu'un classement fixe avec des données nationales et sans
prix. Le prototype technique, lui, est complet et reproductible. Tous les chiffres, avec leurs variantes
acceptables, sont dans le [kit mentor](kit-mentor/README.md#chiffres-de-référence-corrigé).

## Lancer le projet

```bash
uv sync --frozen                         # environnement exact (Python 3.12, versions de uv.lock)
uv run pytest                            # tests (aucune donnée brute ni réseau nécessaire)
uv run agrireco all                      # prepare → train → evaluate (≈ 1 min) ; données téléchargées et vérifiées
uv run mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db     # explorer les runs (http://127.0.0.1:5000)
docker compose up --build                # API (http://localhost:8000/docs) + interface (http://localhost:8501)
```

Sans Docker : `uv run uvicorn api.main:app` puis `uv run streamlit run app/app.py`.

Régénérer tous les supports après une modification du code :

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb pedagogie/*.ipynb
uv run python scripts/rapport_metier.py           # le notebook 02 rejoue le pipeline et refait les captures MLflow
uv run python scripts/capture_interface.py        # captures de l'interface (Chrome nécessaire)
cd presentation && npm ci && npm run build
```

## Organisation

```text
├── PLAN.md                 protocole figé avant les résultats (relu deux fois par le statisticien)
├── config.yaml             configuration unique du pipeline (graine, découpage, variables, plages d'hyperparamètres)
├── src/agrireco/           io (téléchargement + SHA-256), prepare (fusion, noms de pays), synthetic (ACP, effets),
│                           split, metrics, modeling (modèles, règle de sélection), recommend, domain, train (MLflow),
│                           evaluate, service (paquet servi), cli (commande agrireco), viz
├── tests/                  tables construites à la main, API (TestClient), interface sans ML, configuration
├── notebooks/              01 exploration, fusion, ACP · 02 modélisation, MLflow, test, recommandation
├── api/                    FastAPI (main.py), Dockerfile, requirements.txt (généré depuis uv.lock)
├── app/                    Streamlit (app.py), Dockerfile, requirements.txt
├── models/model.joblib     modèle servi (Ridge, quelques Ko) avec références et domaine de validité
├── docs/ci_cd.md           le workflow commenté (étapes, déclencheurs, échecs, secrets)
├── livrables/              rapport métier (HTML et PDF)
├── scripts/                captures MLflow, rapport PDF, captures de l'interface (Chrome sans interface)
├── pedagogie/              01 maille · 02 jointures · 03 ACP · 04 validation par pays · 05 optimisation et MLflow
│                           06 pipeline et YAML · 07 FastAPI · 08 Dockerfile et workflow · 09 cultures incomparables
├── kit-mentor/             repères, séances, questions, erreurs, grille, soutenance
├── presentation/           support de soutenance (.pptx généré) et figures
├── site/                   page interactive pour les apprenants
├── data/processed/         CSV consolidé, journaux, selection.json, resultats.json, tables détaillées, export MLflow
└── data/raw/               données brutes (non versionnées, téléchargées et vérifiées automatiquement)
```

## Ce qui a changé par rapport au plan

| Plan | Réalité | Pourquoi |
|---|---|---|
| Variante de variables « tout sauf pesticides » | remplacée par « culture + pesticides », **après** le premier lancement des variantes | la variante prévue était identique, par erreur, à « culture + pluie + température » ; les variantes ne servent à aucune sélection |
| Test regardé une fois, pour le modèle retenu | analyse complémentaire ajoutée après la sélection : validation aléatoire contre par pays pour chaque famille, et recommandation des arbres optimisés sur le test | montrer que l'optimisme de la validation aléatoire vient des modèles flexibles, et vérifier qu'un modèle non additif ne recommande pas mieux. Elle dessert le choix : la forêt fait 0,566 au test contre 0,608 pour Ridge (écart dans le bruit), sans mieux recommander |
| API : signaler les cultures hors du domaine observé | elle les **relègue** aussi en fin de classement | Ridge classait l'igname en tête même à 8 °C. Règle produit décidée après les résultats ; évaluée à titre exploratoire : 40,9 % de bonne 1ʳᵉ place, sans différence discernable avec le classement fixe |
| Biais, normaliseur, sensibilité | ajouts demandés par le statisticien à la relecture des résultats : biais sur les 20 tirages, intervalle de l'écart avec l'autre normaliseur, égalités dans la sensibilité, nombre de pays où modèle et classement fixe diffèrent (7 sur 24), facteur typique d'erreur | chaque chiffre publié doit avoir une source dans `resultats.json` ; aucun ne change la conclusion |
| Données agrégées par culture du jeu simulé (« proxy » d'irrigation et de fertilisation) | décrites seulement (effets de la simulation), comparées par écart-type | la relecture pédagogique a montré que les coefficients bruts cachaient le poids de la pluie (1,3 t/ha par écart-type contre 0,75 pour l'engrais) |

## Limites

- **Données nationales et annuelles** : pluie constante par pays, pesticides en tonnes nationales ; le modèle ne dit
  rien d'une parcelle (sophisme écologique). Niveau technique de 1990-2013.
- **24 pays de test** : chiffres sensibles au tirage (RMSE-log de 0,51 à 0,67 ; signe du biais instable).
- **Recommandation** évaluée seulement parmi les cultures déjà pratiquées dans chaque pays ; une culture jamais
  cultivée dans des conditions proches n'a pas de vérité terrain.
- **Pas de prix** : aucune conclusion de rentabilité.
- **Ridge retenu à un cheveu** (0,0065 d'écart moyen pour une erreur-type de 0,0068) ; avec d'autres plis, la forêt
  pourrait l'être, sans changer la conclusion sur la recommandation.
- **CI/CD** : le workflow est écrit et ses étapes testées en local (tests, build, conteneur appelé, échecs simulés) ;
  son premier run réel aura lieu au push. Le réentraînement n'est pas automatisé (choix délibéré, voir
  [docs/ci_cd.md](docs/ci_cd.md)).
