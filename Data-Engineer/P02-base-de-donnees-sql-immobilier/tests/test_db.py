"""Tests de la base SQLite construite à partir des petits jeux de conftest.py."""

import sqlite3

import pandas as pd
import pytest

from dataimmo.db import DB_PATH, create_database, query
from dataimmo.prepare import prepare_tables


@pytest.fixture
def tables(sources):
    return prepare_tables(sources)


@pytest.fixture
def base(tmp_path, tables):
    path = tmp_path / "test.sqlite"
    controle = create_database(path, tables, csv_dir=tmp_path)
    return path, controle


def test_control_compares_csv_and_database_rows(base):
    _, controle = base
    assert controle["table"].tolist() == ["region", "commune", "bien", "vente"]
    assert controle["lignes_csv"].tolist() == [4, 4, 5, 5]
    assert controle["lignes_base"].tolist() == [4, 4, 5, 5]


def test_csv_written_with_comma_and_utf8(base, tmp_path):
    lignes = (tmp_path / "commune.csv").read_text(encoding="utf-8").splitlines()
    entete = "id_codedep_codecommune,id_region,code_departement,code_commune,nom_commune,population"
    assert lignes[0] == entete
    assert "972229,02,972,229,Schœlcher,20000" in lignes


def test_csv_leaves_missing_values_empty(base, tmp_path):
    vente = (tmp_path / "vente.csv").read_text(encoding="utf-8").splitlines()
    assert vente[4] == "4,4,2020-06-30,,1"  # Ajaccio : valeur foncière absente => champ vide
    bien = (tmp_path / "bien.csv").read_text(encoding="utf-8").splitlines()
    assert bien[2].startswith("2,01103,,,,LE BOURG,01170,")  # n° de voie, BTQ, type de voie vides


def test_missing_values_are_sql_null_not_empty_text(base):
    path, _ = base
    for table, col, nb_null in [
        ("vente", "valeur_fonciere", 1),
        ("bien", "no_voie", 1),
        ("bien", "btq", 4),
        ("bien", "type_voie", 1),
        ("bien", "code_postal", 1),
    ]:
        compte = query(
            path,
            f"SELECT SUM({col} IS NULL) AS nulls, SUM({col} = '') AS vides, "
            f"SUM(typeof({col}) = 'text' AND {col} = 'nan') AS nan_texte FROM {table}",
        ).iloc[0]
        assert compte["nulls"] == nb_null, col
        assert compte["vides"] == 0, col
        assert compte["nan_texte"] == 0, col


def test_codes_are_stored_as_text(base):
    path, _ = base
    types = query(
        path,
        "SELECT typeof(id_region) AS r, typeof(code_departement) AS d, typeof(code_commune) AS c, "
        "typeof(population) AS p FROM commune WHERE id_codedep_codecommune = '01103'",
    ).iloc[0]
    assert types.tolist() == ["text", "text", "text", "integer"]
    assert query(path, "SELECT id_region FROM region ORDER BY id_region")["id_region"].iloc[0] == "02"


def test_foreign_keys_are_enforced(tmp_path, tables):
    tables["bien"].loc[0, "id_codedep_codecommune"] = "99999"
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        create_database(tmp_path / "fk.sqlite", tables, csv_dir=tmp_path)


def test_type_local_check(tmp_path, tables):
    tables["bien"].loc[0, "type_local"] = "Terrain"
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        create_database(tmp_path / "check.sqlite", tables, csv_dir=tmp_path)


def test_one_vente_per_bien(tmp_path, tables):
    tables["vente"].loc[1, "id_bien"] = 1
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        create_database(tmp_path / "unique.sqlite", tables, csv_dir=tmp_path)


def test_rebuild_replaces_existing_database(base, tables, tmp_path):
    path, _ = base
    controle = create_database(path, tables, csv_dir=tmp_path)
    assert controle["lignes_base"].tolist() == [4, 4, 5, 5]


def test_query_returns_dataframe_and_is_read_only(base):
    path, _ = base
    resultat = query(path, "SELECT type_local, COUNT(*) AS n FROM bien GROUP BY type_local ORDER BY 1")
    assert isinstance(resultat, pd.DataFrame)
    assert resultat.to_dict("list") == {"type_local": ["Appartement", "Maison"], "n": [4, 1]}
    with pytest.raises(pd.errors.DatabaseError, match="readonly"):
        query(path, "DELETE FROM vente")


def test_query_on_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        query(tmp_path / "absente.sqlite", "SELECT 1")


REAL_DB_MISSING = "base réelle non construite (uv run python -m dataimmo.build)"


@pytest.mark.skipif(not DB_PATH.exists(), reason=REAL_DB_MISSING)
def test_real_database_counts_and_nulls():
    comptes = query(
        DB_PATH,
        "SELECT (SELECT COUNT(*) FROM region) AS region, (SELECT COUNT(*) FROM commune) AS commune, "
        "(SELECT COUNT(*) FROM bien) AS bien, (SELECT COUNT(*) FROM vente) AS vente, "
        "(SELECT COUNT(*) FROM vente WHERE valeur_fonciere IS NULL) AS sans_valeur, "
        "(SELECT COUNT(*) FROM vente WHERE valeur_fonciere = '') AS valeur_vide",
    ).iloc[0]
    assert comptes.to_dict() == {
        "region": 19,
        "commune": 3125,
        "bien": 34169,
        "vente": 34169,
        "sans_valeur": 18,
        "valeur_vide": 0,
    }


def test_failed_build_leaves_no_half_built_database(tmp_path, tables):
    path = tmp_path / "ratee.sqlite"
    tables["vente"].loc[1, "id_bien"] = 1
    with pytest.raises(sqlite3.IntegrityError):
        create_database(path, tables, csv_dir=tmp_path)
    assert not path.exists()
