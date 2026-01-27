"""Dessine le schéma relationnel à partir de sql/schema.sql : la figure ne peut pas diverger de la base.

Nécessite Graphviz (commande `dot`) installé sur la machine.
"""

import shutil
import sqlite3
import subprocess
from pathlib import Path

from dataimmo.io import PROJECT_DIR

SCHEMA_PATH = PROJECT_DIR / "sql" / "schema.sql"
FIGURE_PATH = PROJECT_DIR / "presentation" / "figures" / "schema_relationnel.png"
ORDRE = ["vente", "bien", "commune", "region"]
ENCRE, ACCENT, CLE, FOND, GRIS = "#14212e", "#2a78d6", "#c4521f", "#eef3f8", "#4a5866"


def lire_schema(schema_path: Path = SCHEMA_PATH) -> dict[str, dict]:
    """Colonnes, clés primaires et étrangères, colonnes UNIQUE : lues par SQLite lui-même."""
    connexion = sqlite3.connect(":memory:")
    connexion.executescript(schema_path.read_text(encoding="utf-8"))
    tables = {}
    for table in ORDRE:
        colonnes = [(nom, type_sql, bool(pk)) for _, nom, type_sql, _, _, pk in connexion.execute(
            f"PRAGMA table_info({table})")]  # fmt: skip
        etrangeres = {
            de: vers for _, _, vers, de, *_ in connexion.execute(f"PRAGMA foreign_key_list({table})")
        }
        uniques = set()  # une clé étrangère UNIQUE donne une relation 1-1 (une vente par bien)
        for _, index, unique, *_ in connexion.execute(f"PRAGMA index_list({table})"):
            if unique:
                uniques |= {nom for *_, nom in connexion.execute(f"PRAGMA index_info({index})")}
        tables[table] = {"colonnes": colonnes, "fk": etrangeres, "uniques": uniques}
    return tables


def _table_html(table: str, info: dict) -> str:
    entete = f'<font color="white"><b> {table} </b></font>'
    rangees = [f'<tr><td colspan="2" bgcolor="{ACCENT}" align="left">{entete}</td></tr>']
    for nom, type_sql, pk in info["colonnes"]:
        if pk:
            marque, couleur, texte = "PK", CLE, f"<b>{nom}</b>"
        elif nom in info["fk"]:
            marque, couleur, texte = f"FK → {info['fk'][nom]}", ACCENT, nom
        else:
            marque, couleur, texte = "", ENCRE, nom
        rangees.append(
            f'<tr><td align="left" port="{nom}_g"><font color="{couleur}">{texte}</font></td>'
            f'<td align="left" port="{nom}_d"><font color="{GRIS}">{type_sql}  {marque}</font></td></tr>'
        )
    corps = "".join(rangees)
    return (f'<<table border="1" cellborder="0" cellspacing="0" cellpadding="5" color="{ENCRE}" '
            f'bgcolor="{FOND}">{corps}</table>>')  # fmt: skip


def en_dot(tables: dict[str, dict]) -> str:
    lignes = [
        "digraph schema {",
        '  graph [rankdir=LR, bgcolor="white", pad=0.3, nodesep=0.5, ranksep=1.2, fontname="Helvetica"];',
        '  node [shape=plain, fontname="Helvetica"];',
        f'  edge [color="{ENCRE}", penwidth=1.4, fontname="Helvetica", fontsize=12, fontcolor="{CLE}"];',
    ]
    for table, info in tables.items():
        lignes.append(f"  {table} [label={_table_html(table, info)}];")
    for table, info in tables.items():
        for colonne, cible in info["fk"].items():
            cle_cible = next(nom for nom, _, pk in tables[cible]["colonnes"] if pk)
            depart = "1" if colonne in info["uniques"] else "N"
            lignes.append(
                f"  {table}:{colonne}_d:e -> {cible}:{cle_cible}_g:w "
                f'[taillabel="{depart}", headlabel="1", arrowhead=none, labeldistance=1.8];'
            )
    lignes.append("}")
    return "\n".join(lignes)


def dessiner(chemin: Path = FIGURE_PATH) -> Path:
    if shutil.which("dot") is None:
        raise RuntimeError("Graphviz n'est pas installé (commande `dot` introuvable).")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", str(chemin)], input=en_dot(lire_schema()),
                   text=True, check=True)  # fmt: skip
    return chemin


if __name__ == "__main__":
    print(dessiner())
