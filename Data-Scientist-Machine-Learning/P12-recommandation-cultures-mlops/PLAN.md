# PLAN — P12 Data Scientist ML « Concevez un système de recommandations pour une agriculture optimisée par les données »

Plan figé **avant** d'entraîner le moindre modèle retenu (méthode : explorer → planifier → coder → vérifier →
committer). Les écarts constatés pendant la réalisation sont consignés dans le README, section « Ce qui a changé par
rapport au plan ».

## Question métier

Agritech Answers veut une application web pour ses clients agriculteurs, avec deux fonctions :
1. **Prédire** le rendement d'une culture choisie à partir des conditions de la parcelle (température, pluie,
   pesticides).
2. **Recommander** une culture : à partir des seules conditions, simuler toutes les cultures et les classer.

Questions auxquelles le corrigé répond :
- Quelle erreur peut-on attendre sur le rendement d'un **pays que le modèle n'a jamais vu** ?
- Le classement des cultures proposé fait-il mieux qu'un classement au hasard ?
- Quelles variables comptent, et que peut-on honnêtement en dire à un agriculteur ?

## Ce que l'exploration a déjà établi

- **Agriculture Crop Yield** (`crop_yield.csv`, 1 000 000 lignes, aucune valeur manquante) : jeu **synthétique**.
  Une régression linéaire explique 91,3 % de la variance du rendement avec pluie, température, engrais (+1,50 t/ha)
  et irrigation (+1,20 t/ha). Culture, sol, région et météo n'ont aucun effet : les 6 cultures ont toutes un
  rendement moyen de 4,65 t/ha. Il n'y a **ni pays ni année**.
- **Crop Yield Prediction** (FAO + Banque mondiale, 5 fichiers) : `yield_df.csv` contient 28 242 lignes mais
  seulement **13 130 clés distinctes** (pays, culture, année) : `temp.csv` a plusieurs stations pour certains pays
  (Inde, Brésil, Mexique…), et la jointure les a démultipliées. En reconstruisant la table depuis les 4 fichiers
  bruts (température moyennée par pays et année), on retrouve exactement ces 13 130 clés : 101 pays, 10 cultures,
  1990-2013.
- Les noms de pays diffèrent d'un fichier à l'autre (`United States` / `United States of America`, `Russia` /
  `Russian Federation`, `Vietnam` / `Viet Nam`…) : la jointure d'origine perd ces pays en silence.
- La pluie est **constante par pays** (une seule valeur pour 188 des 192 pays renseignés ; pour les 119 pays de la
  table reconstruite, une seule valeur sur 1990-2013) : elle identifie le pays. La température varie 16 fois plus
  entre pays qu'au sein d'un pays. Les pesticides sont des **tonnes totales par pays**, pas des kg/ha : ils mesurent
  d'abord la taille et l'intensité agricole du pays.
- En reconstruisant avec des noms de pays harmonisés : **15 794 clés, 119 pays** (18 pays récupérés, dont les
  États-Unis, la Russie et la Chine continentale).
- Les rendements ne se comparent pas entre cultures : pomme de terre 16,0 t/ha, soja 1,6 t/ha (médianes sur la table
  reconstruite).
- Essai exploratoire (gradient boosting, log du rendement, réglages par défaut) : R² ≈ 0,90 en validation croisée
  aléatoire, ≈ 0,67 quand on teste sur des pays exclus de l'entraînement, ≈ 0,57 avec la culture seule. Ces chiffres
  ont motivé le protocole ci-dessous ; ils ne sont pas des résultats.

## Protocole (fixé avant de voir les résultats)

### Données et fusion

| Décision | Choix | Justification |
|---|---|---|
| Source du modèle | Table FAO **reconstruite depuis les fichiers bruts** (`yield`, `rainfall`, `pesticides`, `temp`), pas `yield_df.csv` | `yield_df.csv` contient 15 112 lignes en double ; les reconstruire permet de les contrôler et de récupérer les pays perdus |
| Noms de pays | Table de correspondance explicite vers les noms FAO (testée) ; nombre de clés gagnées publié | Une jointure qui perd les États-Unis ou la Russie en silence fausse le modèle |
| Agrégats FAO | « China » (agrégat) retiré si « China, mainland » et Taïwan sont présents séparément ; sinon on garde une seule entité Chine, documentée | Pas de double comptage d'un même territoire |
| Température | Moyenne des stations par pays et année | Une ligne par clé |
| Valeurs `..` de la pluie | Converties en manquantes, lignes retirées (comptées) | Aucune imputation sur la variable expliquée ou ses facteurs sans nécessité |
| Clé unique | (pays, culture, année) vérifiée unique après fusion ; sinon le pipeline s'arrête | Garde-fou contre le retour des doublons |
| Unité | Rendement converti de hg/ha en **t/ha** (÷ 10 000) | Unité parlante pour un agriculteur ; même unité que le jeu synthétique |
| Jeu synthétique | Pas de fusion ligne à ligne. On **démontre** que la seule clé commune (la culture, 4 cultures en commun) apporte des colonnes constantes ; on documente la tentative et on l'écarte | Joindre sans clé commune réelle fabriquerait de l'information. L'énoncé laisse libre de l'exploitation des deux jeux si elle est justifiée |
| Rôle du jeu synthétique | ACP demandée (structure des variables) + estimation des effets engrais et irrigation, présentés comme **issus de données simulées** | Ce sont les seules variables « proxy » d'irrigation et de fertilisation disponibles ; elles ne peuvent pas être injectées dans le modèle FAO (aucune clé, autre population) |
| Livrable CSV | `data/processed/dataset_consolide.csv` : une ligne par (pays, culture, année), colonnes sans redondance | Source de vérité des étapes suivantes |

### Modèle de prédiction

| Décision | Choix | Justification |
|---|---|---|
| Cible | log du rendement (t/ha) ; les métriques sont recalculées en t/ha après retour à l'échelle | Écarts de 1 à 100 entre cultures : le log équilibre les cultures ; une erreur en log ≈ une erreur relative |
| Variables d'entrée | culture (one-hot), température moyenne nationale, pluie normale nationale, log10(pesticides totaux nationaux, en tonnes) | Ce que l'énoncé demande de renseigner. Le pays et l'année ne sont pas des entrées (prédire pour des conditions, et l'année future est hors des données) |
| **Ce que prédit le modèle** | Le rendement **moyen national** d'une culture dans un pays aux conditions données, au niveau technique moyen de 1990-2013. **Pas** le rendement d'une parcelle (sophisme écologique). L'application et le rapport libellent les champs « pays-type » | Les trois variables décrivent le pays, pas la parcelle |
| Variantes de variables | En CV groupée : culture seule · culture + pluie · culture + pluie + température · tout sauf pesticides · tout | Mesure ce que chaque variable ajoute au-delà de la culture ; publié tel quel |
| Découpage | Test = **20 % des pays** tirés au hasard (graine 42 ; vérifier que les 10 cultures y figurent, sinon le dire), mis de côté jusqu'à la fin ; réglages par validation croisée **groupée par pays** (5 plis) sur les 80 % restants | Un même pays a des conditions quasi identiques d'une année sur l'autre : un découpage aléatoire mesure la mémoire, pas la généralisation |
| Contre-exemple | Le même modèle évalué en découpage aléatoire, affiché pour montrer l'optimisme | Notion clé du projet pour l'apprenant |
| Métrique principale | **RMSE du log du rendement** en validation croisée groupée | Une seule métrique de décision, comparable entre cultures |
| Métriques secondaires | MAE en t/ha, R² (log), erreur relative médiane, biais moyen en t/ha, écart entraînement / validation ; sur le test : les mêmes, **par culture**, et une version où chaque pays pèse 1 | Lisibles par le métier ; l'écart signale le surapprentissage ; les gros pays (24 ans × 10 cultures) ne doivent pas masquer les petits |
| Retour à l'échelle | exp(prédiction) estime le rendement **médian** (pas la moyenne) ; on publie le biais moyen en t/ha sur le test et on **ne corrige pas** | Cohérent avec la MAE et l'erreur relative médiane ; une correction unique ne change pas le classement, une correction par culture le changerait |
| Modèles comparés | Référence : médiane de la culture (aucune condition) · régression Ridge · forêt aléatoire · gradient boosting (`HistGradientBoostingRegressor`) | De la référence naïve au modèle non linéaire ; tout dans scikit-learn. Ridge sans interaction est **additif en log** : il donne le même ordre des cultures quelles que soient les conditions (voir Recommandation) |
| Optimisation | `RandomizedSearchCV` (30 tirages, graine 42, CV groupée) sur les deux modèles d'arbres ; chaque tirage est un run MLflow enfant | Recherche systématique demandée par la grille ; 30 tirages suffisent pour 3 à 5 hyperparamètres |
| Règle de sélection | Pour chaque pli, différence de RMSE-log entre chaque modèle et le meilleur ; si la moyenne de ces différences est inférieure à son **erreur-type** (écart-type des différences / √5), on retient le plus simple, dans l'ordre référence < Ridge < forêt aléatoire < gradient boosting | Comparaison appariée (mêmes plis) ; évite de choisir sur un écart dans le bruit. Le meilleur des 30 tirages est légèrement optimiste en CV : le test unique corrige ce point |
| Sensibilité au tirage des pays | Le pipeline complet (avec la configuration retenue) est rejoué sur **20 découpages groupés répétés** des pays ; dispersion de la RMSE-log et du taux de bonne 1ʳᵉ place publiée | Un seul jeu de ~24 pays de test est très variable (RMSE-log de 0,58 à 0,77 selon le tirage, en simulation) |
| Test final | Évalué **une seule fois**, après la sélection ; chiffres publiés tels quels | Un test regardé plusieurs fois devient un jeu de validation |
| Modèle servi | Même configuration réentraînée sur tous les pays, sauvegardée (`models/model.joblib` + modèle MLflow) | Le test a servi à estimer l'erreur ; l'API profite de toutes les données |
| Importance des variables | Permutation sur le jeu de test, par variable d'origine (pas par colonne one-hot), 10 répétitions, **plus** le bloc des 3 variables climat/intrants permuté ensemble ; gain du modèle par rapport au modèle « culture seule » | Formulation imposée : « dégradation du modèle quand on casse le lien d'une variable, pour ce modèle et ces pays de test ; avec des variables corrélées, l'importance se partage de façon arbitraire ; elle ne dit ni le sens ni la taille d'un effet ; celle des pesticides traduit d'abord la taille et l'intensité agricole du pays » |
| Reproductibilité | Graines fixées partout ; configuration centralisée dans `config.yaml` ; versions figées par `uv.lock` | Critère de la grille |

### Recommandation

| Décision | Choix | Justification |
|---|---|---|
| Score de classement | **Rendement relatif** = rendement prédit ÷ rendement de référence de la culture, la référence étant la **médiane des médianes par pays** (pays d'entraînement) | Les t/ha ne se comparent pas entre cultures ; « 1,3 » se lit « 30 % au-dessus de ce qu'on obtient d'habitude pour cette culture ». Médiane des pays pour que les séries longues ne pèsent pas plus. Choix validé par l'utilisateur |
| Sensibilité du normaliseur | Taux de bonne 1ʳᵉ place recalculé avec la médiane des lignes | Vérifie que la conclusion ne dépend pas de ce choix |
| Affichage secondaire | Classement en t/ha brutes, avec avertissement | Demandé littéralement par l'énoncé |
| Rentabilité | Non mesurée (aucun prix dans les données) ; on parle de « culture la mieux adaptée », pas de « la plus rentable » | Ne pas affirmer ce que les données ne permettent pas |
| Évaluation | Sur les pays de test, pour chaque (pays, année) avec au moins 3 cultures observées, on classe **les cultures observées** : la 1ʳᵉ du modèle est-elle celle qui a le meilleur rendement relatif **observé** ? (taux de bonne 1ʳᵉ place) + tau-b de Kendall, moyenné d'abord par pays puis entre pays (ex æquo traités par le tau-b) | Seule vérité terrain disponible : les cultures réellement cultivées. Nombre de pays et de (pays, année) évalués publié |
| Références | (a) hasard (taux attendu = moyenne de 1/k) ; (b) **classement constant** : ordre des cultures selon leur rang moyen de rendement relatif sur les pays d'entraînement, identique pour toutes les conditions ; (c) oracle (gain maximal atteignable) | Le hasard est une référence trop faible : en simulation, le classement constant fait mieux que le modèle (43 % contre 39 %) |
| **Règle de décision (fixée avant)** | Le modèle n'est dit « utile pour recommander » que si la différence de taux de bonne 1ʳᵉ place modèle − classement constant a un IC bootstrap apparié à 95 % entièrement au-dessus de 0. Sinon on l'écrit : « le modèle ne recommande pas mieux qu'un classement fixe des cultures » | Choisir la référence après coup serait du jardin des sentiers qui bifurquent |
| Si le modèle retenu est additif | Si la sélection retient Ridge (ou la référence), la recommandation est constante : on l'écrit noir sur blanc | Un modèle additif en log ne peut pas adapter l'ordre des cultures aux conditions |
| Répartition | Nombre de fois où chaque culture est recommandée sur le test | Montre si la recommandation est concentrée sur 2 ou 3 cultures |
| Gain anticipé | Rendement relatif observé de la culture recommandée − rendement relatif observé moyen des cultures du pays cette année-là, publié avec les trois références (hasard ≈ 0, constant, oracle) | Traduction métier, limitée aux cultures effectivement pratiquées ; ce n'est **pas** un gain économique |
| Biais de sélection | Formulation imposée : « le taux et le gain ne valent que parmi les cultures déjà pratiquées dans le pays ; la recommandation d'une culture jamais cultivée dans des conditions semblables n'est pas évaluée ». L'API signale une culture « hors domaine observé » (aucun pays d'entraînement aux conditions proches ne la cultive) et des conditions hors des plages d'entraînement | Les cultures pratiquées ont été choisies parce qu'elles conviennent ; l'application en classe 10 |
| Incertitude | Bootstrap **par pays** (pays tirés avec remise, 2 000 tirages, graine 0) : RMSE-log du test, taux de bonne 1ʳᵉ place et **différence appariée** modèle − classement constant | ~24 pays de test : un chiffre seul surinterprète ; avec si peu de grappes, l'intervalle percentile couvre un peu moins que 95 % (dit dans les supports) |

### ACP (jeu synthétique, demandée par l'énoncé)

| Décision | Choix | Justification |
|---|---|---|
| Variables | Pluie, température, jours jusqu'à récolte, engrais et irrigation (0/1), **toutes standardisées** ; rendement exclu de l'ACP puis projeté en variable supplémentaire | L'ACP décrit la structure des variables explicatives ; y mettre la cible mélange description et prédiction. Non standardisées, les binaires auraient une variance de 0,25 |
| Lecture | Éboulis des valeurs propres. Si elles sont toutes proches de 1 : « pas de structure, pas de réduction possible » ; les axes sont alors **arbitraires** (toute rotation convient) : on ne lit ni les axes ni le cercle des corrélations | À vérifier, pas à affirmer |
| Variables clés | Effets **bruts** de la régression sur le jeu synthétique (t/ha par unité), présentés comme **des paramètres de la simulation, pas une connaissance agronomique** | L'ACP ne dit pas ce qui prédit la cible : c'est une leçon du projet. Les coefficients standardisés des binaires dépendent de la proportion 50/50 |
| Valeurs impossibles | Rendements négatifs du jeu synthétique comptés et signalés | Contrôle de cohérence attendu à l'étape 1 |
| Confrontation des deux jeux | Synthétique : « l'eau et les intrants comptent, la culture non » ; FAO : « la culture domine ». Conclusion : le jeu synthétique ne décrit pas la réalité agronomique | C'est ce que « valider l'analyse avec le second jeu » permet honnêtement |

## Livrables et emplacement

| Livrable | Chemin | Preuve que c'est fini |
|---|---|---|
| 1 — Captures MLflow (.png) | `presentation/figures/mlflow_*.png` (≥ 3 : liste des runs, comparaison, détail d'un run) | ≥ 2 expériences distinctes ; chiffres visibles identiques à l'export `data/processed/mlflow_runs.csv` ; `mlruns/` non versionné |
| 2 — Notebooks d'entraînement | `notebooks/01_exploration_fusion.ipynb`, `notebooks/02_modelisation_mlflow.ipynb` | Exécutés de bout en bout sans erreur |
| 3 — Pipeline MLOps | `src/agrireco/` (`prepare`, `train`, `evaluate`, une commande chacune, fichiers intermédiaires sur disque) + `config.yaml` + `agrireco all` ; `api/` (FastAPI `main.py` mince, Dockerfile, `requirements.txt` généré depuis `uv.lock`) ; `app/` (Streamlit `app.py`, `requirements.txt`) ; `docker-compose.yml` | `uv run agrireco all` régénère CSV, runs et modèle ; fichier absent ou config invalide → message explicite (testé) ; l'image construite depuis un contexte propre répond sur `/health`, `/predict`, `/recommend` |
| 4 — Pipeline CI/CD | `.github/workflows/dsml-p12-agrireco.yml` (racine, filtre `paths:`) + `docs/ci_cd.md` (schéma, déclencheurs, badge, notifications) | lint → tests unitaires → test d'intégration (conteneur lancé puis appelé) → build → push GHCR sur `main` seulement ; permissions minimales ; `requirements.txt` vérifié synchrone ; une étape qui échoue bloque la suite |
| 5 — Rapport métier (.pdf) | `livrables/rapport_metier.pdf`, généré par script depuis `data/processed/resultats.json` | Lisible par un non-spécialiste ; chaque chiffre du PDF présent dans `resultats.json` (contrôle automatique) |
| CSV consolidé | `data/processed/dataset_consolide.csv` + journal de fusion | Clé unique (testée) ; nombre de lignes, pays, cultures, années cités dans le README |
| Interface sans ML | `app/app.py` | Test : aucun import de scikit-learn, joblib ni `agrireco` |
| Code et tests | `src/agrireco/` + `tests/` | `uv run pytest` vert |
| Supports de mentorat | `pedagogie/`, `kit-mentor/`, `presentation/`, `site/`, `ALLER_PLUS_LOIN.md`, `README.md` | Relus par les subagents, recette du product owner |

## Vérifications

- **Code** : tests sur de petites tables construites à la main (correspondance des noms, unicité de la clé, retour à
  l'échelle, rendement relatif, classement, taux de bonne 1ʳᵉ place) ; tests de l'API avec `TestClient` (entrées
  invalides refusées, culture inconnue refusée, classement trié).
- **Données** : SHA-256 du zip ; nombre de lignes à chaque étape de la fusion ; clé unique.
- **Résultats** : chiffres clés recalculés indépendamment par le statisticien ; aucune fuite entre pays
  d'entraînement et de test (test dédié).

## Hors périmètre

Pas de prix ni de calcul de rentabilité ; pas de causalité (« augmenter les pesticides augmente le rendement » n'est
pas une conclusion permise) ; pas de déploiement réel sur Streamlit Cloud (documenté seulement) ; pas de données
météo à la parcelle. Ces pistes vont dans « aller plus loin ».
