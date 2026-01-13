# Grille d'évaluation commentée

Grille de travail du mentor, reformulée et regroupée par compétence. Pour chaque critère : **ce qu'on vérifie**,
où le trouver dans le livrable, et la section correspondante du [corrigé](../notebooks/projet_edstats_corrige.ipynb)
pour comparer. Cocher au fil de la lecture du travail de l'apprenant.

Légende : 🟢 acquis · 🟠 à consolider (on en parle au bilan, non bloquant) · 🔴 bloquant (à corriger avant validation)

## A. Explorer les données et détecter les anomalies (parties 1 et 2)

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Environnement | Notebook exécuté sans erreur ; pandas, matplotlib et seaborn importés | en-tête |
| ☐ | Maille | L'apprenant sait dire ce que représente une ligne de **chaque** fichier | §1.2 |
| ☐ | Taille | `shape` utilisé pour chaque fichier | §1.1 |
| ☐ | Types | Types identifiés (`dtypes`, `info()`) ; colonnes 100 % vides ignorées ou supprimées | §1.3, §1.5 |
| ☐ | Description adaptée au type | `describe()` pour les colonnes numériques, `value_counts()` pour les catégorielles | §1.6 |
| ☐ | `groupby` pour la qualité | Taux de remplissage par année et par indicateur (un `count()` puis une division suffisent) | §2.3 |
| ☐ | `pivot_table` | Lignes = pays, colonnes = indicateurs, valeurs = agrégat des années | §2.4 |
| ☐ | Lecture de `describe()` | Chaque ligne expliquée ; quartiles interprétés ; présence ou absence de valeurs extrêmes argumentée (moyenne/médiane, min/Q1, max/Q3) | §3.2 |
| ☐ | Distributions | Tracées (seaborn ou matplotlib) et interprétées sans contresens | §3.2 |
| ☐ | Bonnes pratiques | Noms de variables explicites ; pas de hardcoding ; **au moins une fonction** ; **au moins une boucle `for`** | §1.3, §3.2 |

## B. Nettoyer les données

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Doublons | Comptés (`duplicated()`) et supprimés (`drop_duplicates()`) | §1.4 |
| ☐ | Valeurs manquantes | Quantifiées par colonne (`isna().sum()` / `mean()`, ou missingno) | §1.5 |
| ☐ | Traitement des manquants | Cohérent avec le métier (pas de `dropna()` aveugle) | §2.2-2.4 |
| ☐ | Filtres conditionnels | `==`, `!=`, `isin()` utilisés pour retirer les faux pays **et** réduire les indicateurs via la colonne de catégories | §1.7, §2.1 |
| ☐ | Corrélations | Matrice calculée avec pandas, visualisée avec seaborn, **utilisée** pour retirer les redondances (un seuil de 0,7 suffit) | §3.1 |
| ☐ | Pearson / Spearman | Différence expliquée à l'oral | §3.1, fiche 3 |
| ☐ | Markdown | Utilisé avec mesure : titres de section, hypothèses, code peu lisible (pas de roman, pas de silence total) | tout le notebook |

## C. Environnement reproductible

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | uv compris | L'apprenant explique la démarche (`uv init` / `uv add` / `uv sync`) | fin du notebook |
| ☐ | Ça tourne | Le notebook s'exécute dans l'environnement créé à partir de `pyproject.toml` | `pyproject.toml` |

> Test rapide : dans un dossier vide, copier `pyproject.toml` (et `uv.lock` s'il est fourni), lancer `uv sync`,
> puis exécuter le notebook.

## D. Présenter ses résultats

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Contexte métier | Rappelé sans erreur | slide 2 |
| ☐ | Jeux de données | Pour chaque fichier : une phrase, le nombre de lignes, quelques colonnes clés | slide 3 |
| ☐ | Démarche de nettoyage | Chaque étape **chiffrée** (lignes, colonnes, indicateurs supprimés) | slides 4-5 |
| ☐ | Hypothèses data | Seuils défendus de façon raisonnable | slide 5 |
| ☐ | Hypothèses métier | Cohérentes avec academy (cible lycée + université, en ligne) | slides 5-7 |
| ☐ | Graphiques | Titre lisible, axes nommés, pas de décoration superflue (couleurs sans signification) | toutes |
| ☐ | Lien avec l'objectif | Compréhensible par un non-technicien | slides 8-10 |
| ☐ | Storytelling | Au moins un élément : fil conducteur, message par slide, tension (maturité vs croissance)… | ensemble |

## Ce qui est « raisonnable » pour une hypothèse data

Exemples à donner à l'apprenant :
- ✅ « Je garde les indicateurs renseignés pour au moins 60 % des couples (pays, année) : en dessous, la comparaison
  porterait sur une minorité de pays. Le seuil est paramétrable en tête de notebook. »
- ✅ « Je résume 2010-2014 par la médiane, avec au moins 3 années renseignées. »
- ❌ « J'ai pris 50 % parce que c'est la moitié. » (pas de lien avec la donnée)
- ❌ « J'ai supprimé les pays avec des NaN. » (combien ? lesquels ? avec quelles conséquences ?)
