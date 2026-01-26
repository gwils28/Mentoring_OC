"""Petits jeux construits à la main, avec les vrais noms de colonnes des 3 fichiers sources.

4 communes vendues (dont une en Martinique, une en Corse) + 1 commune sans vente, 4 régions.
"""

import pandas as pd
import pytest


@pytest.fixture
def ref():
    return pd.DataFrame(
        {
            "regrgp_nom": ["Province", "Province", "DROM-COM", "Province", "Province"],
            "reg_nom": [
                "Auvergne-Rhône-Alpes",
                "Auvergne-Rhône-Alpes",
                "Martinique",
                "Corse",
                "Provence-Alpes-Côte d'Azur",
            ],
            "reg_code": ["84", "84", "02", "94", "93"],
            "com_code": ["01103", "01001", "972229", "2A004", "06088"],
            "com_nom": ["Chevry", "L'Abergement-Clémenciat", "SchÅ“lcher", "Ajaccio", "Nice"],
            "dep_code": ["1", "1", "972", "2A", "6"],
        }
    )


@pytest.fixture
def pop():
    return pd.DataFrame(
        {
            "CODREG": ["84", "84", "02", "94", "93"],
            "CODDEP": ["01", "01", "972", "2A", "06"],
            "CODCOM": ["103", "001", "229", "004", "088"],
            "COM": ["Chevry", "L'Abergement-Clémenciat", "Schœlcher", "Ajaccio", "Nice"],
            "PMUN": ["714", "779", "20000", "70000", "340000"],
            "PTOT": ["730", "798", "20300", "71000", "345000"],
        }
    )


@pytest.fixture
def dvf():
    return pd.DataFrame(
        {
            "Date mutation": [
                "2020-01-02 00:00:00",
                "2020-03-31 00:00:00",
                "2020-04-01 00:00:00",
                "2020-06-30 00:00:00",
                "2020-02-15 00:00:00",
            ],
            "Nature mutation": ["Vente"] * 5,
            "Valeur fonciere": ["165000", "104792.58", "200000", None, "355680"],
            "No voie": ["347", None, "4", "20", "12"],
            "B/T/Q": [None, None, None, "B", None],
            "Type de voie": ["RUE", None, "BD", "RUE", "AV"],
            "Voie": ["DU CHATEAU", "LE BOURG", "EDOUARD BAUDOIN", "MARCEAU", "JEAN MEDECIN"],
            "Code postal": ["1170", "1170", "97233", None, "6000"],
            "Commune": ["CHEVRY", "CHEVRY", "SCHOELCHER", "AJACCIO", "NICE"],
            "Code departement": ["01", "01", "972", "2A", "06"],
            "Code commune": ["103", "103", "229", "004", "088"],
            "Surface Carrez du 1er lot": ["48.22", "120.5", "39.11", "80.25", "65"],
            "Nombre de lots": ["2", "1", "1", "1", "3"],
            "Type local": ["Appartement", "Maison", "Appartement", "Appartement", "Appartement"],
            "Surface reelle bati": ["48", "121", "40", "82", "66"],
            "Nombre pieces principales": ["3", "5", "1", "3", "2"],
            "Nom de l'acquereur": ["GUIRAO", "HARNOIS", "ROGIER", "DUPONT", "MARTIN"],
        }
    )


@pytest.fixture
def sources(dvf, pop, ref):
    return {"dvf": dvf, "population": pop, "referentiel": ref}
