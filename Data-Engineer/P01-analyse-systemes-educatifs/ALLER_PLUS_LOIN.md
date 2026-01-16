# Aller plus loin : les pratiques actuelles sur les notions de P01

Le projet demande pandas, matplotlib, seaborn et uv. C'est la bonne base. Ce document montre ce que font les équipes
data en 2026 sur les mêmes sujets, pour donner de la perspective aux apprenants rapides ou ouvrir la discussion en
fin de bilan.

Pour chaque thème : **ce qu'on fait dans le projet**, **la pratique actuelle**, et **comment l'essayer** sur EdStats.

---

## 1. Environnement reproductible

| Dans le projet | Pratique actuelle |
|---|---|
| `pyproject.toml` créé avec uv | `pyproject.toml` + **`uv.lock` versionné** + version de Python figée (`.python-version`) ; `uv sync --frozen` en CI |

- **uv** est devenu l'outil standard pour gérer projets et environnements Python : il remplace pip, venv, pip-tools,
  pyenv et Poetry pour la plupart des usages, en beaucoup plus rapide.
- **Qualité automatique** : `ruff` (lint + formatage, un seul outil), lancé avant chaque commit grâce à
  `pre-commit`.
- **Conteneurs de dev** (Dev Containers, Docker) quand l'environnement dépasse Python : base de données, outils
  système.

**Essayer** : `uv run ruff check src` dans ce dossier, puis ajouter un fichier `.pre-commit-config.yaml`.

## 2. Au-delà de pandas : formats et moteurs

| Dans le projet | Pratique actuelle |
|---|---|
| CSV de 326 Mo lu entièrement en mémoire | **Parquet** (stockage en colonnes, typé, compressé) ; moteurs **Polars** ou **DuckDB** |

- **pandas 3** (utilisé ici) active le *copy-on-write* et un vrai type `str` adossé à Arrow : moins de copies
  silencieuses et moins d'avertissements `SettingWithCopyWarning`.
- **Polars** : API de DataFrame en Rust, multi-cœur, avec un mode *lazy* qui optimise toute la requête avant de
  l'exécuter.
- **DuckDB** : du SQL directement sur des CSV ou des Parquet, sans serveur. C'est idéal pour explorer un gros fichier.

**Essayer** (DuckDB) : la proportion de valeurs renseignées par année, sans charger le fichier dans pandas.

```sql
-- uv add duckdb ; puis dans un notebook : duckdb.sql("""…""").df()
SELECT count("2010") / count(*) AS part_2010,
       count("2014") / count(*) AS part_2014
FROM 'data/raw/EdStatsData.csv';
```

Comparer aussi la taille du CSV et celle d'une conversion en Parquet
(`COPY (SELECT * FROM 'data/raw/EdStatsData.csv') TO 'data.parquet'`).

## 3. La qualité de données « as code »

| Dans le projet | Pratique actuelle |
|---|---|
| Vérifications ponctuelles (`duplicated`, `isna`) dans le notebook | **Contrats de données** exécutés à chaque chargement : schémas, contraintes, tests |

- **pandera** : un schéma déclaratif (types, plages, unicité de clé) qui échoue avec un message clair.
- **Great Expectations** et **Soda** : des « attentes » sur les données, avec des rapports, adaptées aux pipelines.
- **Empreinte des fichiers bruts** : ce projet vérifie le SHA-256 du zip (`edstats.io`). Si la source change, on le
  sait avant de publier des chiffres faux.

**Essayer** : un schéma pandera qui garantit qu'aucun (pays, indicateur) n'est en double et que les taux
d'internet sont compris entre 0 et 100.

## 4. Profilage automatique

| Dans le projet | Pratique actuelle |
|---|---|
| `describe()`, `value_counts()`, missingno | Rapports automatiques : **ydata-profiling**, **skrub** (`TableReport`) |

Ces outils produisent en une ligne ce que la partie 1 fait à la main. Il faut savoir le faire à la main d'abord
(c'est l'objectif du projet) ; ensuite, l'outil fait gagner du temps sur chaque nouveau jeu de données.

## 5. Notebooks : versionnés, exécutables, relus

| Dans le projet | Pratique actuelle |
|---|---|
| `.ipynb` exécuté avec `nbconvert` | Notebooks **exécutés en CI**, appariés à un script (`jupytext`) ou réactifs (**marimo**) |

- **Le code réutilisable sort du notebook** pour aller dans un package testé : c'est ce que fait `src/edstats/`.
  Le notebook raconte, et le package calcule.
- **jupytext** : chaque notebook a un jumeau `.py` lisible en *diff* dans une revue de code.
- **marimo** : notebooks réactifs stockés en `.py` pur, sans état caché (l'ordre d'exécution ne peut pas mentir).

## 6. De l'analyse au pipeline (le cœur du métier de Data Engineer)

| Dans le projet | Pratique actuelle |
|---|---|
| Un zip téléchargé une fois, un notebook | **Ingestion automatisée** + couches de données + **orchestration** |

- **Ingestion** : la Banque mondiale expose une API publique (bibliothèque `wbgapi`), qui donne des données à jour
  au lieu d'un export figé en 2018.
- **Architecture en couches** (« médaillon ») : *bronze* = brut immuable (`data/raw/`), *silver* = nettoyé et
  typé, *gold* = tables prêtes pour l'analyse (`data/processed/`). Ce projet en est une version minimale.
- **Transformation en SQL versionné** : dbt (ou SQLMesh), avec des tests sur chaque modèle.
- **Orchestration** : Dagster, Airflow ou Prefect relancent le pipeline, gèrent les dépendances et alertent en cas
  d'échec.

**Essayer** : remplacer le zip par un appel `wbgapi` pour les 5 indicateurs retenus sur 2015-2024, puis comparer le
classement obtenu à celui du corrigé.

## 7. Statistique : ce qui vient après la corrélation

| Dans le projet | Pratique actuelle |
|---|---|
| Pearson / Spearman, seuil 0,7, choix métier | Mesures non linéaires, réduction de dimension, analyse multicritère |

- **Liens non monotones** : l'information mutuelle ou le coefficient **φK** (bibliothèque `phik`) détectent aussi
  les relations en U.
- **Multicolinéarité** : le VIF (*variance inflation factor*) mesure ce qu'une variable apporte en plus de **toutes**
  les autres, pas seulement paire par paire.
- **ACP** : au lieu de garder « internet » comme représentant du bloc développement, on peut construire un indice
  synthétique (1ʳᵉ composante principale).
- **Aide à la décision multicritère** : la moyenne pondérée de rangs est la forme la plus simple ; TOPSIS et AHP
  sont des méthodes formalisées. L'analyse de sensibilité aux poids (faite ici avec 1 000 tirages) reste
  indispensable quelle que soit la méthode.
- **Valeurs extrêmes** : la règle de 1,5 × IQR, ou la MAD (écart absolu médian), plus robuste.

## 8. Visualisation et restitution

| Dans le projet | Pratique actuelle |
|---|---|
| Graphiques matplotlib/seaborn exportés dans un PowerPoint | Graphiques **interactifs**, cartes, palettes accessibles, **storytelling** |

- **Plotly** ou **Altair** pour des graphiques interactifs (survol, zoom) ; une **carte choroplèthe** du score par
  pays parle immédiatement à un public métier.
- **Accessibilité** : palettes lisibles par les personnes daltoniennes, titres qui énoncent le message, pas de
  couleur sans signification. Ce sont les règles appliquées aux figures de ce corrigé.
- **Storytelling** : la structure « contexte → tension → résolution » (voir `presentation/README.md`) ; la
  référence classique est *Storytelling with Data* de Cole Nussbaumer Knaflic.
- Pour un usage récurrent : un tableau de bord (Streamlit, Evidence, Superset) plutôt qu'un PowerPoint.

## 9. L'IA générative dans le workflow data

À ce stade du parcours, on déconseille à l'apprenant de faire écrire son code par une IA : le projet sert à
construire les réflexes de base. En entreprise, les assistants de code font pourtant partie du quotidien. La
compétence attendue n'est donc pas « savoir s'en passer », mais **savoir vérifier**.

- Les supports de ce dossier ont été produits avec Claude Code, selon une méthode explicite : plan écrit avant le
  code, tests écrits d'abord, données hashées, chaque chiffre des supports vérifié sur une sortie réelle, et chaque
  commit relu par un humain ([article](https://gwils28.github.io/posts/claude-code-data-science/)).
- Exemple concret tiré de ce projet : une première version de `redundant_pairs` passait ses tests mais plantait
  sur la vraie matrice de corrélation, car l'index et les colonnes portaient le même nom. Le bug a été reproduit
  par un test avant d'être corrigé. Une IA, comme un humain, écrit du code plausible : **seuls les tests et les
  vérifications sur les vraies données disent s'il est juste**.
- Les affirmations aussi se vérifient : plusieurs formulations des supports (« la Chine vaut 1 en min-max »,
  « Pearson s'effondre ») ont été corrigées après comparaison avec les sorties réelles.

## 10. Intégration continue

| Dans le projet | Pratique actuelle |
|---|---|
| Tests lancés à la main | **GitHub Actions** : à chaque push, `uv sync --frozen`, `ruff`, `pytest`, exécution des notebooks |

**Essayer** : un fichier `.github/workflows/ci.yml` d'une vingtaine de lignes qui installe uv, synchronise
l'environnement et lance `pytest`. Le badge vert dans le README devient une preuve de reproductibilité.
