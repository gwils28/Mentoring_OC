"""Point d'entrée : uv run python -m dataimmo.build

Télécharge (si besoin) et vérifie les sources, prépare les 4 tables, construit data/processed/dataimmo.sqlite,
écrit les CSV de chargement et affiche le contrôle des volumes.
"""

from dataimmo.db import DB_PATH, create_database
from dataimmo.io import load_sources
from dataimmo.prepare import prepare_tables, repair_names


def main() -> None:
    sources = load_sources()
    tables = prepare_tables(sources)
    controle = create_database(DB_PATH, tables, csv_dir=DB_PATH.parent)

    ref = sources["referentiel"]
    _, nb_referentiel = repair_names(ref["com_nom"])
    vendues = ref[ref["com_code"].isin(tables["commune"]["id_codedep_codecommune"])]
    _, nb_vendues = repair_names(vendues["com_nom"])

    print(f"Base : {DB_PATH} ({DB_PATH.stat().st_size / 1e6:.1f} Mo)")
    print(f"Noms de communes réparés (encodage) : {nb_vendues} sur {len(vendues)} communes de la base")
    print(f"  (et {nb_referentiel} sur les {len(ref)} communes du référentiel complet)")
    print(controle.to_string(index=False))


if __name__ == "__main__":
    main()
