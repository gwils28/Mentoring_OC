# Erreurs fréquentes

Chaque erreur : comment la repérer, pourquoi elle arrive, quoi faire (avec la fiche qui l'enseigne).

## Données

| Erreur | Repérage | Pourquoi | Remède |
|---|---|---|---|
| Travailler sur `yield_df.csv` tel quel | 28 242 lignes ; l'Inde pèse 13 % des lignes de blé | La table fournie a des doublons (stations de température) | Vérifier la clé (pays, culture, année), agréger la température avant la jointure ([fiche 1](../pedagogie/01_maille_et_doublons.ipynb)) |
| Pays perdus aux jointures | Pas de États-Unis, Russie, Chine, Iran… dans la table finale | Noms différents selon la source ; une jointure ne signale rien | Anti-jointure, table de correspondance ([fiche 2](../pedagogie/02_joindre_sans_perdre.ipynb)) |
| Colonne ` Area` introuvable | `KeyError: 'Area'` sur `rainfall.csv` | Espace au début du nom de colonne | `df.columns.str.strip()` |
| Pluie en texte | dtype `object`/`str`, valeurs `..` | Valeur manquante codée `..` par la Banque mondiale | `pd.to_numeric(..., errors="coerce")` puis décision sur les manquants |
| Unités mélangées | Rendements de l'ordre de 30 000 | La FAO donne des hg/ha | Diviser par 10 000 pour des t/ha |
| Fusion inventée avec le jeu synthétique | « North » associé à des pays, ou colonnes constantes ajoutées | L'énoncé suggère une clé pays/année qui n'existe pas | Faire afficher les colonnes ajoutées par culture ; accepter une fusion écartée **avec démonstration** |

## ACP

| Erreur | Repérage | Pourquoi | Remède |
|---|---|---|---|
| ACP non standardisée | CP1 ≈ 99 % de la variance | La pluie en mm a une variance énorme | `StandardScaler` avant ([fiche 3](../pedagogie/03_ce_que_dit_une_acp.ipynb)) |
| Axes interprétés malgré un éboulis plat | « CP1 = intrants, CP2 = climat » | Envie de trouver une structure | Montrer que CP1 change d'une moitié du jeu à l'autre |
| Variables clés tirées de l'ACP | « l'ACP montre que l'irrigation compte » | Confusion description / prédiction | Une régression ou une importance par permutation répond à cette question |

## Modélisation et MLflow

| Erreur | Repérage | Pourquoi | Remède |
|---|---|---|---|
| Découpage aléatoire | R² ≥ 0,9, forêt « excellente » | Les années d'un même pays se ressemblent : le modèle reconnaît le pays | `GroupKFold` par pays, test sur des pays mis de côté ([fiche 4](../pedagogie/04_valider_sur_des_pays_jamais_vus.ipynb)) |
| Pas de référence | Un score seul (« RMSE 2,4 t/ha ») | Habitude de comparer les modèles entre eux seulement | Médiane par culture comme référence ([fiche 5](../pedagogie/05_optimiser_et_tracer_avec_mlflow.ipynb)) |
| Modèle évalué sur le test pendant le réglage | Le score de test « s'améliore » au fil des essais | Le test devient un jeu de validation | Réglage en CV sur l'entraînement, test regardé une fois |
| RMSE en t/ha toutes cultures confondues | Erreurs dominées par la pomme de terre et le manioc | Échelles de 1 à 13 entre cultures | Log du rendement, ou métriques par culture |
| Captures MLflow illisibles | Liste de runs sans colonnes de métriques, noms « smiling-owl-42 » | Colonnes non ajoutées, runs non nommés | Nommer les runs, ajouter les colonnes, une vue *Compare* ; exporter les runs en CSV |
| Une seule expérience | Un run par modèle, aucune recherche | Confusion entre « essayer 3 modèles » et « optimiser » | `RandomizedSearchCV` / `GridSearchCV`, un run par essai |
| Graine oubliée | Scores qui changent à chaque exécution | `random_state` non fixé | Graine dans la configuration, passée à tous les modèles et découpages |
| Modèle picklé qui ne se recharge pas | Erreur au démarrage de l'API ou dans Docker | Version de scikit-learn (ou de pandas/pyarrow) différente | Versions figées identiques à l'entraînement et dans l'image ; test de rechargement |

## Pipeline, API, Docker, CI

| Erreur | Repérage | Pourquoi | Remède |
|---|---|---|---|
| Tout dans un notebook | Pas de commande pour relancer une étape | Habitude de l'exploration | Fonctions `preparer / entrainer / evaluer` + YAML ([fiche 6](../pedagogie/06_un_pipeline_pilote_par_un_yaml.ipynb)) |
| Chemins absolus | `C:\Users\…` dans le code | Code écrit sur un seul poste | Chemins relatifs au projet, dans la configuration |
| API sans validation | Une température de 300 °C donne une prédiction | Paramètres en `dict` ou en query string sans contrôle | Modèle Pydantic avec bornes ([fiche 7](../pedagogie/07_servir_un_modele_avec_fastapi.ipynb)) |
| ML dans l'interface | `import sklearn` dans `app.py` | Plus simple à court terme | L'interface appelle l'API, rien d'autre |
| Image Docker qui ne démarre pas | `ModuleNotFoundError` dans les journaux du conteneur | Dépendance absente de `requirements.txt` (pyarrow pour un objet pandas picklé, par exemple) | `requirements.txt` généré depuis l'environnement verrouillé ; conteneur lancé et appelé dans la CI |
| Workflow au mauvais endroit | Rien ne se déclenche | Le YAML n'est pas dans `.github/workflows/` à la racine du dépôt | Déplacer ; filtre `paths:` si plusieurs projets |
| Secret dans le YAML | `docker login -p …` en clair | Méconnaissance des secrets GitHub | Secrets du dépôt ou `GITHUB_TOKEN` ([fiche 8](../pedagogie/08_lire_un_dockerfile_et_un_workflow.ipynb)) |
| Publication sans tests | Image publiée alors que les tests échouent | Jobs indépendants | `needs: tests` |
| CI qui veut réentraîner sans données | Job en échec sur un fichier absent | `data/raw` non versionné | Tester et emballer un modèle versionné ; réentraînement hors CI (ou données téléchargées et vérifiées) |
| Nom d'image GHCR refusé | `repository name must be lowercase` | Propriétaire avec majuscules | Mettre le nom en minuscules |

## Recommandation et rapport

| Erreur | Repérage | Pourquoi | Remède |
|---|---|---|---|
| Classement par t/ha | La pomme de terre ou le manioc toujours en tête | Les t/ha ne se comparent pas entre cultures | Rendement relatif ([fiche 9](../pedagogie/09_comparer_des_cultures_incomparables.ipynb)) |
| « Culture la plus rentable » | Le mot rentabilité sans prix | Reprise de l'énoncé | Dire que les prix manquent ; ajouter des prix externes justifiés, ou parler de « culture la mieux adaptée » |
| Comparé au hasard seulement | « 2× mieux que le hasard » | Référence trop facile | Comparer à un classement fixe (fiche 9) |
| Causalité | « augmenter les pesticides augmente le rendement » | Corrélation entre pays (taille, équipement) lue comme un effet | Reformuler : « les pays qui utilisent plus de pesticides ont… » ; données nationales |
| Rapport technique | RMSE, R², GroupKFold dans un rapport pour décideurs | Habitude du notebook | Une phrase par résultat, en langage métier ; le détail technique en annexe |
