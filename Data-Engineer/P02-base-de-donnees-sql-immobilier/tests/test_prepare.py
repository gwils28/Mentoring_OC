"""Tests des fonctions de préparation : on connaît la bonne réponse avant d'exécuter."""

import numpy as np
import pandas as pd
import pytest

from dataimmo.prepare import (
    BIEN_COLUMNS,
    COMMUNE_COLUMNS,
    VENTE_COLUMNS,
    build_bien_vente,
    build_commune,
    build_region,
    code_postal,
    commune_key,
    prepare_tables,
    repair_mojibake,
    repair_names,
)

# --- Encodage ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("abime", "attendu"),
    [
        ("SchÅ“lcher", "Schœlcher"),
        ("Pont-Ã\xa0-Bucy", "Pont-à-Bucy"),  # « à » abîmé : Ã suivi d'une espace insécable
        ("VogÃ¼é", "Vogüé"),  # partie abîmée + accent sain dans le même nom
        ("Prévessin-MoÃ«ns", "Prévessin-Moëns"),
        ("Saint-RaphaÃ«l", "Saint-Raphaël"),
    ],
)
def test_repair_mojibake_fixes_utf8_read_as_windows_1252(abime, attendu):
    assert repair_mojibake(abime) == attendu


@pytest.mark.parametrize(
    "sain",
    ["Ajaccio", "L'Abergement-Clémenciat", "Schœlcher", "Œuilly", "L'Haÿ-les-Roses", "Saint-Étienne", "Âge"],
)
def test_repair_mojibake_leaves_healthy_names_unchanged(sain):
    assert repair_mojibake(sain) == sain


def test_repair_mojibake_lets_missing_values_through():
    assert repair_mojibake(None) is None
    assert repair_mojibake(np.nan) is np.nan


def test_repair_names_counts_repaired_names():
    noms = pd.Series(["SchÅ“lcher", "Nice", "Pont-Ã\xa0-Bucy", None])
    repares, nb = repair_names(noms)
    assert repares.tolist()[:3] == ["Schœlcher", "Nice", "Pont-à-Bucy"]
    assert pd.isna(repares.iloc[3])
    assert nb == 2


# --- Codes ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [("1170", "01170"), ("75001", "75001"), (" 6000 ", "06000"), (None, None), (np.nan, None), ("", None)],
)
def test_code_postal_pads_to_five_characters(brut, attendu):
    assert code_postal(brut) == attendu


@pytest.mark.parametrize("invalide", ["123456", "75 001", "2A000"])
def test_code_postal_rejects_invalid_codes(invalide):
    with pytest.raises(ValueError, match=invalide):
        code_postal(invalide)


@pytest.mark.parametrize(
    ("dep", "com", "attendu"),
    [("01", "103", "01103"), ("972", "226", "972226"), ("2A", "004", "2A004"), ("06", "88", "06088")],
)
def test_commune_key(dep, com, attendu):
    assert commune_key(dep, com) == attendu


def test_commune_key_on_columns():
    cles = commune_key(pd.Series(["01", "972", "2B"]), pd.Series(["103", "226", "33"]))
    assert cles.tolist() == ["01103", "972226", "2B033"]


# --- Tables -----------------------------------------------------------------------------------------------


def test_build_region(ref):
    region = build_region(ref)
    assert list(region.columns) == ["id_region", "nom_region", "nom_regroupement"]
    # code INSEE texte : « 02 » garde son zéro
    assert region["id_region"].tolist() == ["02", "84", "93", "94"]
    assert region.set_index("id_region").loc["02", "nom_regroupement"] == "DROM-COM"


def test_build_region_rejects_code_with_two_names(ref):
    ref.loc[1, "reg_nom"] = "Rhône-Alpes"
    with pytest.raises(ValueError, match="84"):
        build_region(ref)


def test_build_commune_keeps_only_communes_sold(dvf, pop, ref):
    commune = build_commune(dvf, pop, ref)
    assert list(commune.columns) == COMMUNE_COLUMNS
    assert commune["id_codedep_codecommune"].tolist() == ["01103", "06088", "2A004", "972229"]
    ligne = commune.set_index("id_codedep_codecommune").loc["972229"]
    assert ligne["nom_commune"] == "Schœlcher"  # nom réparé
    assert ligne["id_region"] == "02"
    assert ligne["code_departement"] == "972"
    assert ligne["code_commune"] == "229"
    assert commune.set_index("id_codedep_codecommune").loc["2A004", "code_departement"] == "2A"


def test_build_commune_population_is_pmun_as_integer(dvf, pop, ref):
    commune = build_commune(dvf, pop, ref).set_index("id_codedep_codecommune")
    assert pd.api.types.is_integer_dtype(commune["population"])
    assert commune.loc["01103", "population"] == 714  # PMUN, pas PTOT (730)


def test_build_commune_raises_when_population_missing(dvf, pop, ref):
    pop = pop[pop["CODCOM"] != "229"]
    with pytest.raises(ValueError, match="972229"):
        build_commune(dvf, pop, ref)


def test_build_commune_raises_when_region_missing(dvf, pop, ref):
    ref = ref[ref["com_code"] != "2A004"]
    with pytest.raises(ValueError, match="2A004"):
        build_commune(dvf, pop, ref)


def test_build_commune_raises_on_duplicated_population_key(dvf, pop, ref):
    pop = pd.concat([pop, pop.iloc[[0]]])
    with pytest.raises(ValueError, match="01103"):
        build_commune(dvf, pop, ref)


def test_build_bien_vente_one_bien_and_one_vente_per_row(dvf, pop, ref):
    bien, vente = build_bien_vente(dvf, build_commune(dvf, pop, ref))
    assert list(bien.columns) == BIEN_COLUMNS
    assert list(vente.columns) == VENTE_COLUMNS
    assert len(bien) == len(vente) == len(dvf)
    assert bien["id_bien"].is_unique and vente["id_vente"].is_unique
    assert vente["id_bien"].tolist() == bien["id_bien"].tolist()
    assert bien["id_codedep_codecommune"].tolist() == ["01103", "01103", "972229", "2A004", "06088"]


def test_build_bien_vente_formats(dvf, pop, ref):
    bien, vente = build_bien_vente(dvf, build_commune(dvf, pop, ref))
    assert bien["code_postal"].tolist()[:3] == ["01170", "01170", "97233"]
    assert pd.isna(bien.loc[3, "code_postal"])
    assert vente["date_vente"].tolist()[:2] == ["2020-01-02", "2020-03-31"]
    assert vente["valeur_fonciere"].dtype == "float64"
    assert vente.loc[1, "valeur_fonciere"] == pytest.approx(104792.58)
    assert pd.isna(vente.loc[3, "valeur_fonciere"])
    assert bien.loc[0, "surface_carrez"] == pytest.approx(48.22)
    assert bien["total_pieces"].tolist() == [3, 5, 1, 3, 2]
    assert vente["nombre_lots"].tolist() == [2, 1, 1, 1, 3]
    assert pd.isna(bien.loc[1, "no_voie"])
    assert bien.loc[0, "no_voie"] == 347


def test_build_bien_vente_drops_buyer_name(dvf, pop, ref):
    """RGPD : le nom de l'acquéreur ne doit survivre ni en colonne ni en valeur."""
    acquereurs = dvf["Nom de l'acquereur"].tolist()
    tables = prepare_tables({"dvf": dvf, "population": pop, "referentiel": ref})
    for nom, table in tables.items():
        assert not any("acquereur" in col.lower() for col in table.columns), nom
        valeurs = set(table.astype(str).to_numpy().ravel())
        assert valeurs.isdisjoint(acquereurs), nom


def test_build_bien_vente_raises_on_unknown_commune(dvf, pop, ref):
    communes = build_commune(dvf, pop, ref)
    communes = communes[communes["id_codedep_codecommune"] != "06088"]
    with pytest.raises(ValueError, match="06088"):
        build_bien_vente(dvf, communes)


def test_prepare_tables_returns_tables_in_loading_order(sources):
    tables = prepare_tables(sources)
    assert list(tables) == ["region", "commune", "bien", "vente"]
    assert [len(t) for t in tables.values()] == [4, 4, 5, 5]


def test_build_region_keeps_insee_code_and_source_name(ref):
    """Code INSEE en texte ; le nom « Ile-de-France » (sans accent) est gardé tel que la source l'écrit."""
    idf = pd.DataFrame(
        {
            "regrgp_nom": ["Ile-de-France"],
            "reg_nom": ["Ile-de-France"],
            "reg_code": ["11"],
            "com_code": ["75056"],
            "com_nom": ["Paris"],
            "dep_code": ["75"],
        }
    )
    region = build_region(pd.concat([ref, idf], ignore_index=True)).set_index("id_region")
    assert region.loc["11", "nom_region"] == "Ile-de-France"
    assert region.index.map(type).unique().tolist() == [str]


def test_build_bien_vente_keeps_surface_reelle_bati(dvf, pop, ref):
    bien, _ = build_bien_vente(dvf, build_commune(dvf, pop, ref))
    assert bien["surface_reelle_bati"].tolist() == [48, 121, 40, 82, 66]


def test_build_commune_normalise_les_espaces_multiples(dvf, pop, ref):
    # le référentiel écrit « Marseille  1er » ou « Paris  7e » avec deux espaces
    ref.loc[ref["com_code"] == "06088", "com_nom"] = "Nice  Centre "
    commune = build_commune(dvf, pop, ref).set_index("id_codedep_codecommune")
    assert commune.loc["06088", "nom_commune"] == "Nice Centre"
