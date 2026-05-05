# Aller plus loin — pratiques actuelles du marché

Chaque piste part d'une limite du corrigé et indique comment l'essayer sur ce projet. Elles ne sont pas exigées
par la grille : ce sont des sujets de discussion pour la soutenance (« comment iriez-vous en production ? ») et des
idées pour les apprenants à l'aise.

## 1. Du rendement à la rentabilité : ajouter des prix

**Limite du corrigé.** Aucune donnée de prix : on classe par rendement relatif, jamais par revenu.

**Pratique.** Joindre les **prix producteurs** de FAOSTAT (domaine *Prices*, par pays, culture et année, en devise
locale et en dollars) pour estimer un revenu par hectare = rendement × prix, puis soustraire des coûts de production
quand on en dispose. Attention aux pièges : devises et inflation (travailler en dollars constants), prix manquants
pour les cultures vivrières peu commercialisées (manioc, igname), et prix qui varient plus d'une année à l'autre que
les rendements.

**L'essayer.** Télécharger l'export FAOSTAT des prix producteurs, le vérifier par empreinte comme les autres
données, ajouter une étape `prepare` qui le joint (même harmonisation des noms de pays), et un champ
`critere: "rendement" | "revenu"` dans la requête `/recommend`. Garder la même règle de décision : battre un classement fixe des cultures.

## 2. Des données à la parcelle

**Limite du corrigé.** Pluie constante par pays, pesticides en tonnes nationales : le modèle prédit un rendement
moyen national.

**Pratique.** Les applications agronomiques actuelles combinent des données **météo réanalysées** (ERA5 / ERA5-Land
du programme européen Copernicus : précipitations et températures horaires, aussi disponibles en agrégats
quotidiens, sur une grille d'environ 9 km pour ERA5-Land et 31 km pour ERA5),
des **cartes de sols** (SoilGrids) et des **images satellite** (Sentinel-2, indices de végétation comme le NDVI), à la
maille de la parcelle ou de la région, plus les déclarations des exploitants (intrants, irrigation, rendement
obtenu).

**L'essayer.** Remplacer la pluie « normale » par le cumul de la saison de culture de l'année (ERA5 agrégé par pays
et année) : la pluie redevient une variable qui change d'une année à l'autre, et l'on peut mesurer si elle apporte
enfin quelque chose en validation par pays.

## 3. Optimisation d'hyperparamètres plus efficace

**Limite du corrigé.** `RandomizedSearchCV`, 30 tirages indépendants : simple et défendable, mais chaque tirage
ignore les précédents.

**Pratique.** **Optuna** (recherche bayésienne par TPE, arrêt précoce des essais peu prometteurs) est devenu un
standard ; il s'intègre à MLflow (un run par essai). **LightGBM** ou **XGBoost** offrent plus d'options (GPU,
contraintes, variables catégorielles natives) ; à ce volume (moins de 16 000 lignes),
`HistGradientBoostingRegressor`, inspiré de LightGBM, suffit.

**L'essayer.** Remplacer `_search` et la boucle de `run_search` dans `train.py` par une étude Optuna de 30 essais
sur les mêmes plis groupés (un run MLflow enfant par essai, ou `optuna_integration.mlflow.MLflowCallback`) ; pour
l'arrêt précoce, rapporter le score pli par pli (`trial.report`) avec un *pruner*. Comparer dans MLflow le meilleur
score obtenu à budget égal.

## 4. Un registre de modèles et des alias

**Limite du corrigé.** Le modèle servi est un fichier versionné dans git (`models/model.joblib`), choisi à la main.

**Pratique.** Le **Model Registry** de MLflow donne un nom au modèle, numérote ses versions et leur attribue des
**alias** (`champion`, `challenger`) : l'API charge `models:/agrireco@champion`, et promouvoir un modèle revient à
déplacer l'alias, sans modifier le code ni reconstruire l'image (il suffit de redémarrer le service). On y attache la signature d'entrée, les métriques de test et la version
des dépendances.

**L'essayer.** Dans `evaluate.py`, ajouter `registered_model_name="agrireco"` à l'appel
`mlflow.sklearn.log_model(served, name="modele", ...)` existant, puis poser l'alias avec
`MlflowClient().set_registered_model_alias("agrireco", "champion", info.registered_model_version)`. Le modèle seul
ne suffit pas à l'API : enregistrer aussi le paquet (`model.joblib`, avec les références et le domaine) comme
artefact du run. Dans l'API, si `MLFLOW_TRACKING_URI` est définie, charger par alias, sinon le fichier local
(`mlflow` rejoint alors les dépendances de l'image). La promotion prend effet au prochain redémarrage du service.

## 5. Versionner les données et automatiser le réentraînement

**Limite du corrigé.** Les données brutes sont vérifiées par empreinte mais pas versionnées ; le réentraînement est
manuel.

**Pratique.** **DVC** versionne les données et les sorties d'un pipeline (fichiers lourds hors de git, empreintes
dans git) et ne relance que les étapes dont les entrées ont changé (`dvc repro`). Les orchestrateurs (Airflow,
Prefect, Dagster, ou un simple workflow GitHub programmé) déclenchent le réentraînement à l'arrivée de nouvelles
données ; un **critère de promotion** décide si le nouveau modèle remplace l'ancien (meilleur sur un test récent,
et toujours meilleur qu'un classement fixe).

**L'essayer.** Écrire un `dvc.yaml` à trois étapes (`prepare`, `train`, `evaluate`) qui reprend les commandes
`agrireco` ; puis un workflow GitHub `on: schedule` qui télécharge les données, rejoue le pipeline et ouvre une pull
request avec le nouveau `resultats.json` pour relecture humaine (droits `contents: write` et `pull-requests: write`).
Attention : une pull request ouverte avec `GITHUB_TOKEN` ne lance pas la CI ; il faut un jeton d'application GitHub
ou un jeton personnel.

## 6. Surveiller le modèle en production

**Limite du corrigé.** L'API signale les conditions hors des plages vues, mais rien n'est collecté.

**Pratique.** On surveille trois choses : la **santé** du service (latence, erreurs : Prometheus et Grafana, ou
l'outil du cloud), la **dérive des entrées** (les conditions envoyées s'éloignent-elles de celles de
l'entraînement ? tests statistiques par variable, par exemple avec **Evidently**), et la **performance réelle** quand
les vrais rendements arrivent (une saison plus tard en agriculture : la surveillance des entrées est donc le
premier signal disponible).

**L'essayer.** Journaliser chaque requête de l'API (entrées, prédiction, indicateurs hors domaine) dans un fichier
ou une base ; générer chaque semaine un rapport de dérive qui compare ces entrées aux données d'entraînement : avec
Evidently dans un environnement séparé (au 25/10/2026, il ne s'importe pas avec pandas 3 :
`uv run --no-project --with evidently --with "pandas<3" …`), ou simplement avec un test de Kolmogorov-Smirnov par
variable (`scipy.stats.ks_2samp`).

## 7. Dire l'incertitude, pas seulement un chiffre

**Limite du corrigé.** L'API renvoie un rendement ponctuel ; l'erreur typique (37 %) n'apparaît que dans le rapport.

**Pratique.** Renvoyer un **intervalle de prédiction** : régression quantile (`HistGradientBoostingRegressor(loss=
"quantile", quantile=0.1)` et `0.9`) ou **prédiction conforme** (bibliothèque MAPIE), qui garantit une couverture
moyenne choisie (par exemple 80 %) sous une hypothèse faible : les pays sont interchangeables. Ici, la calibration doit se faire **par pays** (plis
groupés), sinon la couverture annoncée est fausse pour un nouveau pays.

**L'essayer.** Ajouter à `/predict` un champ `intervalle_80` calculé avec
`mapie.regression.CrossConformalRegressor(confidence_level=0.8, conformity_score="gamma", cv=GroupKFold(...))` et
`fit_conformalize(X, y, groups=pays)` (le score « gamma » mesure des erreurs relatives et évite les bornes
négatives), puis vérifier sur les pays de test qu'environ 80 % des rendements réels tombent dedans.

## 8. Industrialiser l'image et le déploiement

**Limite du corrigé.** Image publiée sur GHCR, déploiement de l'interface seulement documenté.

**Pratique.**
- **Héberger l'API** sur un service de conteneurs managé (Google Cloud Run, Azure Container Apps, AWS App Runner,
  Render…) : on pousse l'image, le service la lance et la met à l'échelle ; l'interface Streamlit pointe vers son
  adresse publique.
- **Sécuriser la chaîne** : analyse des vulnérabilités de l'image (Trivy, Grype) dans la CI, inventaire des
  dépendances (SBOM), signature de l'image (cosign, sans clé grâce à l'OIDC de GitHub Actions : le job a besoin de
  `permissions: id-token: write`) ; épingler les actions GitHub par empreinte (SHA) plutôt que par
  tag.
- **Images plus rapides à construire** : installer avec `uv` dans le Dockerfile
  (`COPY --from=ghcr.io/astral-sh/uv:<version> /uv /bin/`, puis
  `uv sync --locked --no-default-groups --group api --no-install-project`) : lecture directe de `uv.lock`, plus
  besoin de `api/requirements.txt` ni de l'étape de CI qui vérifie sa synchronisation.
- **Prévenir l'équipe** : une étape Slack ou Teams dans le job d'alerte du workflow.

**L'essayer.** Ajouter après le build une étape `aquasecurity/trivy-action`, épinglée par SHA (l'action a été
brièvement compromise en mars 2026, avis GHSA-69fq-xp46-6x23), avec `image-ref: agrireco-api:ci`,
`severity: CRITICAL` et `exit-code: "1"` : le job échoue sur une vulnérabilité critique ; déployer l'image sur un service gratuit ou peu coûteux et renseigner `API_URL` dans les
secrets de Streamlit Community Cloud.

## 9. Documenter le modèle

**Pratique.** Une **fiche de modèle** (*model card*) résume en une page : usage prévu (rendement moyen national,
pas parcelle), données et période (1990-2013), métriques sur données jamais vues, limites connues (variables
nationales, pas de prix, recommandation qui ne bat pas un classement fixe), et quand ne pas l'utiliser. C'est aussi
ce que demandent les cadres réglementaires récents pour les systèmes d'IA (documentation et transparence).

**L'essayer.** Générer `MODEL_CARD.md` depuis `resultats.json` à la fin de `evaluate`, et l'enregistrer comme
artefact MLflow du run final.
