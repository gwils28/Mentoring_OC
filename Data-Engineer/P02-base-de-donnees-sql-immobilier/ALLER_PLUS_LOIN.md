# Aller plus loin : les pratiques actuelles sur les notions de P02

Le projet demande un schéma relationnel, une base SQLite, 12 requêtes SQL et une réflexion sur la sauvegarde et le
RGPD. C'est la bonne base. Ce document montre ce que font les équipes data en 2026 sur les mêmes sujets, pour donner
de la perspective aux apprenants rapides ou ouvrir la discussion en fin de bilan.

Pour chaque thème : **ce qu'on fait dans le projet**, **la pratique actuelle**, et **comment l'essayer** sur la base
DATAImmo. Tous les essais ont été exécutés sur ce projet ; les chiffres cités en sortent.

Mode d'emploi des essais :
- les commandes se lancent **depuis le dossier du projet**, après avoir construit la base
  (`uv run python -m dataimmo.build`) ;
- un bloc Python s'enregistre dans un fichier d'essai **hors de `src/`** (par exemple `essai.py` à la racine), puis
  se lance avec `uv run python essai.py` ; quand un outil supplémentaire est nécessaire, on l'ajoute pour la seule
  commande avec `uv run --with <outil>`, sans toucher à `pyproject.toml` ;
- on ne modifie jamais la base livrée : les essais qui écrivent travaillent sur une copie, dans le dossier
  temporaire du système.

---

## 1. SQLite ou serveur de base de données

| Dans le projet | Pratique actuelle |
|---|---|
| **SQLite** : un fichier, pas de serveur ; DDL écrit « compatible PostgreSQL autant que possible » | **PostgreSQL** (ou un autre serveur) dès que plusieurs personnes écrivent en même temps, souvent lancé dans un **conteneur Docker** en développement et confié à un service managé en production |

- **SQLite suffit** pour un POC, un seul utilisateur, une base surtout lue, ou une application embarquée. C'est le
  choix recommandé par l'énoncé, et il est juste ici.
- **Un serveur devient utile** quand il faut plusieurs écritures simultanées, des **droits par utilisateur** (qui
  voit quoi : un vrai sujet RGPD), une sauvegarde continue ou de gros volumes.
- **« Compatible » se vérifie en exécutant.** L'essai ci-dessous charge le schéma et les 4 CSV dans PostgreSQL :
  - le schéma passe une fois la ligne `PRAGMA` retirée (elle n'existe qu'en SQLite) ;
  - `\copy ... CSV` lit les champs vides comme `NULL` : les 18 ventes sans valeur foncière sont bien `NULL`, sans
    le piège du texte vide des outils graphiques ;
  - **5 requêtes sur 12 échouent** (04, 05, 08, 10, 11) : `ROUND(x, 0)` n'existe pas en PostgreSQL pour un nombre
    à virgule flottante. Écriture qui marche dans les deux moteurs (vérifiée, 3 745 €/m² des deux côtés) :
    `ROUND(CAST(AVG(v.valeur_fonciere / b.surface_carrez) AS NUMERIC), 0)` ;
  - **piège silencieux** : `REAL` vaut 8 octets en SQLite mais **4 octets en PostgreSQL** (environ 7 chiffres
    significatifs). Résultat : 184 valeurs foncières arrondies au chargement, jusqu'à 5 centimes d'écart
    (4 098 416,20 € stocké 4 098 416,25 €). Pour un montant, on choisit `DOUBLE PRECISION` ou `NUMERIC(12, 2)`.

**Essayer** (Docker requis ; commandes pour bash, Linux ou macOS) :

```bash
docker run -d --rm --name dataimmo-pg -e POSTGRES_PASSWORD=essai \
  -v "$PWD/data/processed:/data:ro" -v "$PWD/sql:/sql:ro" postgres:17
until docker exec dataimmo-pg pg_isready -h localhost -U postgres; do sleep 1; done
grep -v PRAGMA sql/schema.sql | docker exec -i dataimmo-pg psql -U postgres -v ON_ERROR_STOP=1
for t in region commune bien vente; do
  docker exec dataimmo-pg psql -U postgres -c "\copy $t FROM '/data/$t.csv' CSV HEADER"
done
docker exec dataimmo-pg psql -U postgres -f /sql/requetes/05_prix_m2_maison_ile_de_france.sql   # échoue : ROUND
docker stop dataimmo-pg   # le conteneur et ses données disparaissent (option --rm)
```

## 2. DuckDB : du SQL directement sur les fichiers

| Dans le projet | Pratique actuelle |
|---|---|
| pandas lit les xlsx, prépare les tables, puis on les charge dans SQLite pour les interroger | **DuckDB** interroge directement un xlsx, un CSV, un Parquet ou une base SQLite, sans import ni serveur |

- **Pour explorer avant de modéliser** : on vérifie un volume ou un taux de remplissage sur le fichier brut en une
  requête, sans écrire de code de préparation.
- **Pour l'analyse** : DuckDB est un moteur analytique (stockage en colonnes) avec une vraie fonction `median()`,
  absente de SQLite.
- **Il ne remplace pas la base du projet** : SQLite (ou PostgreSQL) garde les contraintes et sert l'application ;
  DuckDB sert à analyser.
- Les extensions `excel` et `sqlite` de DuckDB se téléchargent au premier usage : il faut une connexion internet.
- Le fichier DVF a des colonnes de types mélangés (B/T/Q, codes `2A`) : `all_varchar = true` lit tout en texte,
  comme le fait le corrigé avec `dtype=str`.

**Essayer** : `uv run --with duckdb python essai.py`, avec ce contenu. On retrouve les 18 valeurs manquantes
(2 791 − 2 789 et 31 378 − 31 362) et la moyenne (3 745) et la médiane (3 244) du besoin 5, sur 1 059 maisons.

```python
import duckdb

# 1. Le fichier Excel brut, sans pandas ni import : all_varchar évite les erreurs de typage (B/T/Q, codes 2A)
duckdb.sql("""
    SELECT "Type local", count(*) AS ventes, count("Valeur fonciere") AS avec_valeur
    FROM read_xlsx('data/raw/Valeurs-foncières.xlsx', all_varchar = true)
    GROUP BY ALL
""").show()

# 2. La base SQLite du projet, ouverte en lecture seule, avec une vraie fonction median()
duckdb.sql("ATTACH 'data/processed/dataimmo.sqlite' AS immo (TYPE sqlite, READ_ONLY)")
duckdb.sql("""
    SELECT round(avg(v.valeur_fonciere / b.surface_carrez)) AS moyenne,
           round(median(v.valeur_fonciere / b.surface_carrez)) AS mediane,
           count(*) AS n
    FROM immo.vente AS v
    JOIN immo.bien AS b USING (id_bien)
    JOIN immo.commune AS c USING (id_codedep_codecommune)
    WHERE b.type_local = 'Maison' AND c.id_region = '11' AND v.valeur_fonciere IS NOT NULL
""").show()
```

## 3. Fonctions de fenêtre : médiane et top N par groupe

| Dans le projet | Pratique actuelle |
|---|---|
| `RANK() OVER (...)` dans les besoins 8 et 11 ; médiane calculée en pandas, faute de `MEDIAN` dans SQLite | Médiane écrite en SQL avec des fonctions de fenêtre, ou fonction native (`PERCENTILE_CONT` en PostgreSQL, `median()` en DuckDB) ; filtre `QUALIFY` pour le top N |

- **Médiane en SQL standard** : on numérote les lignes triées (`ROW_NUMBER()`), on compte le groupe
  (`COUNT(*) OVER ()`) et on garde la ou les deux lignes du milieu. Même résultat que pandas : 3 244 €/m².
- **Top N par groupe** : `ROW_NUMBER()` donne exactement N lignes ; `RANK()` (choix du corrigé) garde les
  ex aequo, donc parfois plus de N lignes ; `DENSE_RANK()` ne saute pas de rang après des ex aequo. Le choix se
  justifie, comme le reste.
- **`QUALIFY`** (DuckDB et d'autres moteurs analytiques, pas SQLite ni PostgreSQL) filtre sur une fonction de
  fenêtre sans sous-requête : le besoin 11 tient en une requête, avec les 15 mêmes communes que le corrigé.
- **La version de SQLite compte** : le SQLite livré avec le Python du projet (vérifié : 3.46) n'a pas `median()` ;
  le client `sqlite3` d'une image Docker Alpine récente (vérifié : 3.53) l'a. Pour un livrable, on ne compte pas sur
  une fonction qui dépend de la version installée chez le lecteur.

**Essayer** : enregistrer cette requête dans `mediane.sql` à la racine du projet, puis
`uv run python -c "from pathlib import Path; from dataimmo.db import query, DB_PATH; print(query(DB_PATH, Path('mediane.sql').read_text(encoding='utf-8')))"`.
Résultat attendu : 3244 sur 1 059 maisons, comme le notebook. Refaire ensuite le calcul par département
(`PARTITION BY` dans les deux `OVER`).

```sql
-- Médiane du prix au m² des maisons d'Île-de-France (besoin 5), sans fonction MEDIAN
WITH prix AS (
    SELECT
        v.valeur_fonciere / b.surface_carrez AS prix_m2,
        ROW_NUMBER() OVER (ORDER BY v.valeur_fonciere / b.surface_carrez) AS rang,
        COUNT(*) OVER () AS n
    FROM vente AS v
    INNER JOIN bien    AS b ON b.id_bien = v.id_bien
    INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
    WHERE b.type_local = 'Maison'
      AND c.id_region = '11'
      AND v.valeur_fonciere IS NOT NULL
)
SELECT ROUND(AVG(prix_m2), 0) AS prix_m2_median, MAX(n) AS n
FROM prix
WHERE rang IN ((n + 1) / 2, (n + 2) / 2);   -- 1 ligne si n est impair, les 2 du milieu si n est pair
```

## 4. Index et plan d'exécution

| Dans le projet | Pratique actuelle |
|---|---|
| Aucun index ajouté : seuls ceux créés automatiquement par `PRIMARY KEY` et `UNIQUE` existent | On **lit le plan d'exécution** (`EXPLAIN QUERY PLAN` en SQLite, `EXPLAIN ANALYZE` en PostgreSQL), on indexe les colonnes de jointure et de filtre, et on **mesure** avant et après |

- **Ni SQLite ni PostgreSQL n'indexent automatiquement une clé étrangère.** Sans index sur
  `bien.id_codedep_codecommune`, retrouver les biens d'une commune oblige à parcourir toute la table.
- **Mesure sur le besoin 11** (5 départements) : sans index, le plan commence par `SCAN v` (les 34 169 ventes) ;
  avec un index sur `commune(code_departement)` et un sur `bien(id_codedep_codecommune)`, il part des communes des
  5 départements (`SEARCH c USING INDEX`). Durée : environ 10 ms, puis 2,5 ms.
- **Un index a un coût** : de la place sur disque et des insertions plus lentes. À 34 000 lignes, le gain ne se voit
  pas ; il compte quand la base accueillera les autres années et toute la France. On indexe ce que les requêtes
  utilisent vraiment, pas toutes les colonnes.

**Essayer** : `uv run python essai.py`, avec ce contenu (il travaille sur une copie de la base).

```python
import shutil
import sqlite3
import tempfile
import timeit
from pathlib import Path

copie = Path(tempfile.gettempdir()) / "dataimmo_essai.sqlite"
shutil.copy("data/processed/dataimmo.sqlite", copie)  # on ne touche jamais à la base livrée
sql = Path("sql/requetes/11_top3_communes_par_departement.sql").read_text(encoding="utf-8")
conn = sqlite3.connect(copie)


def mesurer(titre):
    """Affiche la durée d'une exécution et les lignes du plan qui disent comment les tables sont lues."""
    plan = [ligne[-1] for ligne in conn.execute("EXPLAIN QUERY PLAN " + sql)]
    acces = [etape for etape in plan if etape.startswith(("SCAN v", "SEARCH"))]
    duree = min(timeit.repeat(lambda: conn.execute(sql).fetchall(), number=20, repeat=5)) / 20
    print(f"{titre} : {duree * 1000:.1f} ms", *acces, sep="\n   ")


mesurer("sans index")
conn.execute("CREATE INDEX idx_commune_departement ON commune (code_departement)")
conn.execute("CREATE INDEX idx_bien_commune ON bien (id_codedep_codecommune)")
mesurer("avec index")
```

## 5. Qualité du SQL : un linter

| Dans le projet | Pratique actuelle |
|---|---|
| Requêtes mises en forme à la main, avec un style cohérent | **SQLFluff** (linter et formateur SQL, qui connaît le dialecte SQLite) avec une configuration partagée, lancé en `pre-commit` et en CI, comme `ruff` pour Python |

- **Résultat brut sur `sql/requetes/`** : 90 remarques, **aucune erreur d'analyse** (les 12 requêtes sont du SQL
  valide pour SQLFluff). Ce sont toutes des remarques de style :
  - 42 lignes de plus de 80 caractères (`LT05`) ; le projet a choisi 110, comme pour Python ;
  - 28 alignements et indentations (`LT01`, `LT02`) : les `AS` alignés en colonnes sont un choix de lisibilité ;
  - 12 conditions de jointure écrites `b.id_bien = v.id_bien` au lieu de `v.id_bien = b.id_bien` (`ST09` :
    nommer d'abord la table déjà présente) ;
  - quelques lignes vides attendues après une CTE (`LT08`) et un ordre de colonnes (`ST06`, `LT09`).
- **On ne « corrige » pas tout** : on décide des règles en équipe, on les écrit dans un fichier `.sqlfluff`
  (par exemple `max_line_length = 110`, `exclude_rules = LT01,LT02`), puis l'outil fait respecter ce choix.
- `sqlfluff fix` réécrit les fichiers : à lancer seulement sous contrôle de version, pour relire le *diff*.

**Essayer** : `uvx sqlfluff lint sql/requetes --dialect sqlite`, puis
`uvx sqlfluff lint sql/requetes --dialect sqlite --exclude-rules LT01,LT02,LT05` pour voir ce qui reste une fois
les choix de mise en page du projet assumés.

## 6. Requêtes versionnées et testées

| Dans le projet | Pratique actuelle |
|---|---|
| 12 fichiers `.sql` versionnés ; `tests/test_requetes.py` recoupe chaque requête par un calcul pandas indépendant | **dbt** ou **SQLMesh** : chaque requête devient un « modèle » (table ou vue) ; dépendances, tests, documentation et lignage sont générés |

- **Le recoupement SQL ↔ pandas du projet est déjà une très bonne pratique** : deux chemins de calcul différents
  qui donnent le même résultat. Beaucoup d'équipes ne vont pas jusque-là.
- **Un test dbt est une requête qui doit renvoyer 0 ligne** : les lignes renvoyées sont les erreurs. Par exemple
  `SELECT * FROM vente WHERE date_vente NOT BETWEEN '2020-01-01' AND '2020-06-30'`. dbt fournit aussi des tests
  tout faits : `unique`, `not_null`, `relationships` (clé étrangère), `accepted_values`.
- **À partir de quand ça vaut le coût** : quand des dizaines de requêtes s'enchaînent (une table calculée en
  alimente une autre) et que plusieurs personnes les maintiennent. Pour 12 requêtes indépendantes, `pytest` suffit.
- Pour découvrir sans serveur : dbt fonctionne avec DuckDB grâce à l'adaptateur `dbt-duckdb`
  (`uvx --from dbt-duckdb dbt --version` s'installe bien ; un projet dbt complet n'a pas été testé ici).

**Essayer** : `uv run pytest tests/test_requetes.py -q` (13 tests verts). Puis, dans la requête 08, remplacer
`b.total_pieces > 4` par `b.total_pieces >= 4`, relancer : `test_08_regions_plus_de_4_pieces` échoue. Le test
protège l'interprétation figée dans `PLAN.md`. Annuler ensuite la modification.

## 7. Intégrité et contrats de données

| Dans le projet | Pratique actuelle |
|---|---|
| `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK` dans `schema.sql` ; à la construction, `PRAGMA foreign_key_check` et contrôle des volumes CSV = base | Contraintes au plus près de la donnée **et** **contrat de données** vérifié avant le chargement (pandera, Great Expectations, Soda) ; tables `STRICT` en SQLite |

- **Les contraintes du projet fonctionnent** : sur une copie de la base, un prix négatif, une vente d'un bien
  inexistant et une date `02/01/2020` sont refusés, avec un message qui nomme la règle violée.
- **Deux trous trouvés par l'essai, puis corrigés dans `schema.sql`** (une première version les laissait passer ;
  un test les vérifie désormais) :
  - `'2020-13-45'` passait le contrôle `LIKE '____-__-__'`, qui vérifie la forme, pas la date. Le schéma utilise
    maintenant `CHECK (date(date_vente) IS date_vente)`, qui refuse aussi le 30 février ;
  - un texte vide `''` passait `CHECK (valeur_fonciere > 0)`. SQLite est souple sur les types : il range le texte
    dans une colonne `REAL`, et en SQLite un texte est toujours « plus grand » qu'un nombre. C'est exactement le
    piège des imports par outil graphique. Le schéma vérifie maintenant `typeof(valeur_fonciere) = 'real'` ; autre
    parade possible : une table déclarée `STRICT` (SQLite refuse alors tout texte dans une colonne `REAL`).
  - Ces deux parades sont propres à SQLite ; en PostgreSQL, les types sont stricts d'office (et une colonne `DATE`
    refuse le 13ᵉ mois).
- **Le contrat avant le chargement** : pandera décrit chaque colonne (type, plage, unicité, valeurs manquantes
  permises) et liste **toutes** les lignes fautives, avec leur index. On l'applique aux CSV avant de les charger.

**Essayer** : `uv run python essai.py` (les contraintes, sur une copie), puis `uv run --with pandera python essai.py`
(le contrat sur `vente.csv`), avec ces deux contenus successivement.

```python
import shutil
import sqlite3
import tempfile
from pathlib import Path

copie = Path(tempfile.gettempdir()) / "dataimmo_essai.sqlite"
shutil.copy("data/processed/dataimmo.sqlite", copie)
conn = sqlite3.connect(copie)
conn.execute("PRAGMA foreign_keys = ON")  # sans cette ligne, la clé étrangère n'est pas vérifiée
nouvelle_vente = "INSERT INTO vente (id_bien, date_vente, valeur_fonciere, nombre_lots) VALUES"
essais = {
    "prix négatif": f"{nouvelle_vente} (1, '2020-01-02', -5, 1)",
    "bien inexistant": f"{nouvelle_vente} (999999, '2020-01-02', 1000, 1)",
    "date au format FR": "UPDATE vente SET date_vente = '02/01/2020' WHERE id_vente = 1",
    "date impossible": "UPDATE vente SET date_vente = '2020-13-45' WHERE id_vente = 1",
    "texte vide ''": "UPDATE vente SET valeur_fonciere = '' WHERE id_vente = 1",
}
for nom, sql in essais.items():
    try:
        conn.execute(sql)
        print(f"{nom} : ACCEPTÉ (problème !)")
    except sqlite3.IntegrityError as erreur:
        print(f"{nom} : refusé ({erreur})")
```

```python
import pandas as pd
import pandera.pandas as pa

schema_vente = pa.DataFrameSchema(
    {
        "id_vente": pa.Column(int, unique=True),
        "id_bien": pa.Column(int, unique=True),
        "date_vente": pa.Column(str, pa.Check.str_matches(r"^2020-0[1-6]-\d{2}$")),
        "valeur_fonciere": pa.Column(float, pa.Check.gt(0), nullable=True),
        "nombre_lots": pa.Column(int, pa.Check.ge(1)),
    },
    strict=True,  # une colonne en trop (ex. le nom de l'acquéreur) fait échouer la validation
)
ventes = pd.read_csv("data/processed/vente.csv")
schema_vente.validate(ventes)
print("vente.csv conforme :", len(ventes), "lignes")

ventes.loc[ventes["id_vente"] == 1, "valeur_fonciere"] = -5  # on abîme une copie en mémoire
try:
    schema_vente.validate(ventes, lazy=True)  # lazy : liste toutes les erreurs, pas seulement la 1re
except pa.errors.SchemaErrors as erreurs:
    print(erreurs.failure_cases[["column", "check", "failure_case", "index"]])
```

## 8. Sauvegarde et restauration

| Dans le projet | Pratique actuelle |
|---|---|
| La base se reconstruit à l'identique depuis les sources vérifiées par SHA-256 (`uv run python -m dataimmo.build`) : c'est déjà une forme de sauvegarde | Sauvegarde **cohérente** planifiée (API `backup` ou `.backup` en SQLite, `pg_dump` en PostgreSQL), export SQL texte (`.dump`), **restauration testée**, copies chiffrées hors site (règle 3-2-1 : 3 copies, 2 supports, 1 hors site) |

- **Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde.** L'essai restaure et revérifie volumes,
  intégrité et clés orphelines (19 / 3 125 / 34 169 / 34 169, `ok`, 0).
- **Copier le fichier pendant qu'on écrit dedans** peut donner une copie incohérente ; l'API `backup` de SQLite
  copie un état cohérent.
- **Binaire ou texte** : la copie binaire (3,7 Mo) se restaure en un instant ; le dump SQL (environ 6 Mo) se lit,
  se compare et se rejoue dans un autre moteur, après adaptation.
- **Ordre des tables** : le dump les écrit par ordre alphabétique (`bien` avant `commune`). On restaure donc clés
  étrangères désactivées (le réglage par défaut de SQLite), puis on lance `PRAGMA foreign_key_check`.
- **RGPD** : une sauvegarde contient les mêmes données que la base ; la durée de conservation et la protection
  d'accès s'appliquent aussi aux copies.
- Pour aller plus loin : la réplication continue d'une base SQLite vers un stockage objet (outil **Litestream**,
  non testé ici).

**Essayer** : `uv run python essai.py`, avec ce contenu (la base livrée est ouverte en lecture seule).

```python
import sqlite3
import tempfile
from pathlib import Path

dossier = Path(tempfile.gettempdir())
source = sqlite3.connect("file:data/processed/dataimmo.sqlite?mode=ro", uri=True)

# 1. Copie binaire cohérente, même si quelqu'un écrit dans la base pendant la copie
with sqlite3.connect(dossier / "dataimmo_sauvegarde.sqlite") as copie:
    source.backup(copie)

# 2. Export en SQL texte (CREATE TABLE + INSERT) : lisible, versionnable, rejouable ailleurs
(dossier / "dataimmo_dump.sql").write_text("\n".join(source.iterdump()), encoding="utf-8")

# 3. Restauration : on rejoue le dump dans une base neuve, puis on vérifie les volumes et l'intégrité
restauree = sqlite3.connect(":memory:")
restauree.executescript((dossier / "dataimmo_dump.sql").read_text(encoding="utf-8"))
for table in ["region", "commune", "bien", "vente"]:
    print(table, restauree.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
print("intégrité :", restauree.execute("PRAGMA integrity_check").fetchone()[0])
print("clés orphelines :", len(restauree.execute("PRAGMA foreign_key_check").fetchall()))
```

Avec le client en ligne de commande `sqlite3` (non installé sur toutes les machines ; ici lancé dans un conteneur
Alpine, ce qui a été testé) :

```bash
mkdir -p /tmp/sauvegarde_dataimmo
docker run --rm -v "$PWD/data/processed:/data:ro" -v /tmp/sauvegarde_dataimmo:/out alpine sh -c "
  apk add --no-cache sqlite > /dev/null &&
  sqlite3 -readonly /data/dataimmo.sqlite '.backup /out/sauvegarde.sqlite' &&
  sqlite3 -readonly /data/dataimmo.sqlite .dump > /out/dump.sql &&
  sqlite3 /out/restauree.sqlite < /out/dump.sql &&
  sqlite3 /out/restauree.sqlite 'SELECT COUNT(*) FROM vente; PRAGMA integrity_check;'"
```

Sortie attendue : `34169` puis `ok`. Sous Linux, les fichiers créés par le conteneur appartiennent à `root`.

## 9. RGPD : pseudonymiser n'est pas anonymiser

| Dans le projet | Pratique actuelle |
|---|---|
| La colonne `Nom de l'acquereur` n'est jamais reprise : aucune requête n'en a besoin (minimisation) | Si un besoin exige de relier les achats d'une même personne : **pseudonymisation par hachage salé** (HMAC), sel gardé à part ; sinon, suppression, comme ici |

- **Pseudonymisée** : on remplace le nom par un code, mais quelqu'un qui détient une information supplémentaire
  (le sel, une table de correspondance) peut retrouver la personne. **C'est toujours une donnée personnelle** : le
  RGPD s'applique.
- **Anonymisée** : plus personne ne peut ré-identifier, même en croisant avec d'autres sources. Le RGPD ne
  s'applique plus, mais c'est difficile à garantir.
- **Supprimer le nom ne rend pas la base anonyme** : adresse, date et prix d'une vente permettent de retrouver le
  bien, donc souvent son propriétaire. Le bon mot pour ce projet est **minimisation** : on ne garde que ce qui sert.
- **Un hachage sans sel ne protège rien** : il suffit de hacher une liste de noms (un annuaire) pour tout
  retrouver. L'essai le montre : 100 % des hachages sans sel sont retrouvés.
- **Le sel est un secret** : hors du dépôt Git, dans un gestionnaire de secrets. Qui a le sel peut ré-identifier.
- **Constat sur la donnée** : 11 112 noms distincts pour 34 169 ventes, et 32 280 ventes dont le nom apparaît
  plusieurs fois. Un nom seul n'identifie pas une personne de façon fiable (homonymes), et son pseudonyme pas
  davantage.
- **Piège de lecture** : sans `dtype=str`, pandas lit 4 noms du fichier comme le booléen `False`.

**Essayer** : `uv run python essai.py`, avec ce contenu. Il n'affiche aucun nom, seulement des décomptes.

```python
import hashlib
import hmac
import secrets

import pandas as pd

noms = pd.read_excel("data/raw/Valeurs-foncières.xlsx", usecols=["Nom de l'acquereur"], dtype=str).iloc[:, 0]
# dtype=str : sans lui, 4 noms sont lus comme des booléens False (cellules interprétées par Excel/pandas)

sel = secrets.token_bytes(32)  # le « sel » secret : à ranger hors du dépôt (gestionnaire de secrets), jamais dans le code


def pseudonyme(nom: str) -> str:
    """Même nom -> même pseudonyme (on peut encore compter les achats d'une personne), mais irréversible sans le sel."""
    return hmac.new(sel, nom.encode("utf-8"), hashlib.sha256).hexdigest()[:16]


pseudos = noms.map(pseudonyme)
print("acquéreurs distincts :", noms.nunique(), "| pseudonymes distincts :", pseudos.nunique())
print("ventes dont le nom apparaît plusieurs fois (homonymes ou même personne) :", int(pseudos.duplicated(keep=False).sum()))

# Pourquoi le sel est indispensable : sans lui, il suffit de hacher une liste de noms connus pour tout retrouver.
sans_sel = noms.map(lambda n: hashlib.sha256(n.encode("utf-8")).hexdigest())
annuaire = {hashlib.sha256(n.encode("utf-8")).hexdigest() for n in noms.unique()}  # l'« annuaire » de l'attaquant
print("hachages sans sel retrouvés par l'attaquant :", f"{sans_sel.isin(annuaire).mean():.0%}")
```

## 10. Formats d'échange : Parquet et Arrow

| Dans le projet | Pratique actuelle |
|---|---|
| CSV de chargement (demandés par l'énoncé), relus avec un `dtype` explicite dans les tests | **Parquet** pour échanger entre outils (typé, compressé, stocké en colonnes) ; **Arrow** comme format en mémoire partagé par pandas, Polars et DuckDB |

- **Le CSV perd les types** : relu sans précaution, le code postal `01170` devient le nombre `1170.0`. C'est pour
  cela que `tests/test_requetes.py` précise un `dtype` pour chaque code. Le Parquet garde `'01170'` en texte.
- **Plus léger** : `bien` passe de 2,10 Mo en CSV à 0,90 Mo en Parquet, `vente` de 1,13 Mo à 0,42 Mo.
- **Lecture partielle** : en Parquet, on ne lit que les colonnes utiles, ce qui compte sur de gros fichiers.
- **La suite** : les formats de « lakehouse » (**Delta Lake**, **Apache Iceberg**) ajoutent au-dessus de fichiers
  Parquet des transactions et un historique des versions. Ils valent le coût à partir de gros volumes partagés
  entre équipes, pas pour ce POC.
- Le CSV reste le livrable attendu par l'énoncé ; le Parquet est l'étape suivante.

**Essayer** : `uv run --with duckdb --with pyarrow python essai.py`, avec ce contenu.

```python
import tempfile
from pathlib import Path

import duckdb
import pandas as pd

dossier = Path(tempfile.gettempdir())
duckdb.sql("ATTACH 'data/processed/dataimmo.sqlite' AS immo (TYPE sqlite, READ_ONLY)")
for table in ["commune", "bien", "vente"]:
    duckdb.sql(f"COPY immo.{table} TO '{dossier / table}.parquet' (FORMAT parquet)")
    taille_csv = Path(f"data/processed/{table}.csv").stat().st_size
    taille_parquet = (dossier / f"{table}.parquet").stat().st_size
    print(f"{table:8} CSV {taille_csv / 1e6:5.2f} Mo | Parquet {taille_parquet / 1e6:5.2f} Mo")

# Le Parquet garde les types : relu sans précaution, le CSV transforme le code postal « 01170 » en 1170.0
print("CSV     :", pd.read_csv("data/processed/bien.csv")["code_postal"].head(1).tolist())
print("Parquet :", pd.read_parquet(dossier / "bien.parquet")["code_postal"].head(1).tolist())
```
