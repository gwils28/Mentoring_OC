"""Création de la base SQLite DATAImmo, export des CSV de chargement et contrôle des volumes."""

import sqlite3
from pathlib import Path

import pandas as pd

from dataimmo.io import PROCESSED_DIR, PROJECT_DIR

SCHEMA_PATH = PROJECT_DIR / "sql" / "schema.sql"
DB_PATH = PROCESSED_DIR / "dataimmo.sqlite"
TABLE_ORDER = ["region", "commune", "bien", "vente"]  # parents avant enfants, à cause des clés étrangères


def write_csv(tables: dict[str, pd.DataFrame], csv_dir: Path) -> dict[str, Path]:
    """Écrit un CSV par table (virgule, UTF-8) ; une valeur manquante devient un champ vide.

    Attention à l'import de ces CSV dans un outil graphique (SQLite Studio, DB Browser) : le champ vide y est
    chargé comme texte vide '' et non comme NULL. Il faut alors corriger après import, par exemple
    UPDATE vente SET valeur_fonciere = NULL WHERE valeur_fonciere = '';
    (idem pour bien.no_voie, btq, type_voie, code_postal).
    Sinon COUNT, AVG et IS NULL donnent de faux résultats.
    """
    csv_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name in TABLE_ORDER:
        paths[name] = csv_dir / f"{name}.csv"
        tables[name].to_csv(paths[name], index=False, encoding="utf-8")
    return paths


def insert_rows(conn: sqlite3.Connection, table: str, df: pd.DataFrame) -> None:
    """Insère les lignes d'un DataFrame dans une table déjà créée par schema.sql (avec ses contraintes).

    On écrit l'INSERT nous-mêmes plutôt que df.to_sql : pandas masquerait le message de SQLite
    (« FOREIGN KEY constraint failed », « CHECK constraint failed… ») derrière une erreur générique.
    """
    colonnes = ", ".join(df.columns)
    marqueurs = ", ".join("?" * len(df.columns))  # un « ? » par colonne : SQLite insère les valeurs lui-même
    # astype(object) donne des int/float Python (que sqlite3 sait écrire) ;
    # where(...) remplace NaN/NA par None, que sqlite3 écrit NULL.
    valeurs = df.astype(object).where(df.notna(), None)
    conn.executemany(
        f"INSERT INTO {table} ({colonnes}) VALUES ({marqueurs})", valeurs.itertuples(index=False)
    )


def create_database(path: Path, tables: dict[str, pd.DataFrame], csv_dir: Path) -> pd.DataFrame:
    """(Re)crée la base (schema.sql), charge les 4 tables, écrit les CSV, renvoie le contrôle des volumes.

    Lève une erreur si une contrainte est violée au chargement ou si un volume CSV diffère de la base.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)  # on repart d'une base vide : relancer donne toujours le même résultat
    csv_paths = write_csv(tables, csv_dir)

    conn = sqlite3.connect(path)
    try:
        with conn:  # une transaction : tout est chargé, ou rien (annulation à la première erreur)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            for name in TABLE_ORDER:
                insert_rows(conn, name, tables[name])
        orphelines = conn.execute("PRAGMA foreign_key_check").fetchall()
        lignes_base = [conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in TABLE_ORDER]
    except sqlite3.Error:
        conn.close()
        path.unlink()  # pas de base à moitié construite qu'on prendrait pour la bonne
        raise
    conn.close()  # « with conn » valide la transaction mais ne ferme pas la connexion

    if orphelines:
        raise ValueError(f"{len(orphelines)} clé(s) étrangère(s) orpheline(s), ex. {orphelines[:5]}")

    controle = pd.DataFrame(
        {
            "table": TABLE_ORDER,
            # on relit le CSV (et non le DataFrame) : c'est bien le fichier livré que l'on contrôle
            "lignes_csv": [len(pd.read_csv(csv_paths[name], dtype=str)) for name in TABLE_ORDER],
            "lignes_base": lignes_base,
        }
    )
    ecarts = controle[controle["lignes_csv"] != controle["lignes_base"]]
    if not ecarts.empty:
        raise ValueError(f"Volumes CSV et base différents :\n{ecarts.to_string(index=False)}")
    return controle


def build_database(path: Path = DB_PATH) -> pd.DataFrame:
    """Construit la vraie base depuis les fichiers sources ; les CSV sont écrits à côté de la base."""
    # imports locaux : tester create_database ne demande ni le téléchargement ni la lecture des xlsx
    from dataimmo.io import load_sources
    from dataimmo.prepare import prepare_tables

    return create_database(path, prepare_tables(load_sources()), csv_dir=path.parent)


def query(path: Path, sql: str) -> pd.DataFrame:
    """Exécute une requête et renvoie le résultat en DataFrame. Base ouverte en lecture seule."""
    path = Path(path)
    if not path.exists():
        # sans ce contrôle, sqlite3 créerait silencieusement une base vide
        raise FileNotFoundError(
            f"Base introuvable : {path} (la construire : uv run python -m dataimmo.build)"
        )
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()
