"""Tests de la fusion FAO sur de petites tables construites à la main."""

import pandas as pd
import pytest

from agrireco import prepare


def _yield(rows):
    return pd.DataFrame(rows, columns=["Area", "Item", "Year", "Value"]).assign(Unit="hg/ha")


def test_harmonize_maps_aliases_to_fao_names():
    s = pd.Series(["United States", "Russia", "Peru", "South Korea "])
    assert prepare.harmonize(s).tolist() == [
        "United States of America",
        "Russian Federation",
        "Peru",
        "Republic of Korea",
    ]


def test_china_climate_goes_to_mainland_and_aggregate_is_dropped():
    y = _yield([("China", "Rice, paddy", 2000, 60000), ("China, mainland", "Rice, paddy", 2000, 62000)])
    rain = pd.DataFrame({"Area": ["China"], "Year": [2000], "average_rain_fall_mm_per_year": ["645"]})
    pest = pd.DataFrame({"Area": ["China, mainland"], "Year": [2000], "Value": [1000.0]})
    temp = pd.DataFrame({"country": ["China", "China"], "year": [2000, 2000], "avg_temp": [10.0, 12.0]})
    out, _ = prepare.build_fao_table(y, rain, pest, temp)
    assert out["country"].tolist() == ["China, mainland"]
    assert out["avg_temp"].iloc[0] == pytest.approx(11.0)


def test_build_fao_table_averages_stations_and_converts_units():
    y = _yield([("Peru", "Maize", 2000, 30000), ("Peru", "Potatoes", 2000, 120000)])
    rain = pd.DataFrame({"Area": ["Peru"], "Year": [2000], "average_rain_fall_mm_per_year": ["1738"]})
    pest = pd.DataFrame({"Area": ["Peru"], "Year": [2000], "Value": [4000.0]})
    temp = pd.DataFrame({"country": ["Peru"] * 3, "year": [2000] * 3, "avg_temp": [18.0, 20.0, 22.0]})
    out, log = prepare.build_fao_table(y, rain, pest, temp)
    assert len(out) == 2  # 3 stations n'ont pas triplé les lignes
    assert out.set_index("crop").loc["Maize", "yield_t_ha"] == pytest.approx(3.0)
    assert out["avg_temp"].tolist() == [20.0, 20.0]
    assert out["rainfall_mm"].dtype == float
    assert list(log.columns) == ["etape", "lignes"]


def test_rainfall_placeholder_is_dropped_not_imputed():
    y = _yield([("Peru", "Maize", 2000, 30000), ("Peru", "Maize", 2001, 31000)])
    rain = pd.DataFrame(
        {"Area": ["Peru", "Peru"], "Year": [2000, 2001], "average_rain_fall_mm_per_year": ["..", "1738"]}
    )
    pest = pd.DataFrame({"Area": ["Peru"] * 2, "Year": [2000, 2001], "Value": [4000.0, 4100.0]})
    temp = pd.DataFrame({"country": ["Peru"] * 2, "year": [2000, 2001], "avg_temp": [19.0, 19.5]})
    out, _ = prepare.build_fao_table(y, rain, pest, temp)
    assert out["year"].tolist() == [2001]


def test_check_unique_key_raises_on_duplicates():
    df = pd.DataFrame({"country": ["Peru", "Peru"], "crop": ["Maize", "Maize"], "year": [2000, 2000]})
    with pytest.raises(ValueError, match="clé"):
        prepare.check_unique_key(df)


def test_crop_join_with_synthetic_adds_near_constant_columns():
    fao = pd.DataFrame({"crop": ["Maize", "Rice, paddy", "Potatoes"], "yield_t_ha": [3.0, 4.0, 18.0]})
    agri = pd.DataFrame(
        {
            "Crop": ["Maize", "Maize", "Rice", "Rice", "Cotton"],
            "Fertilizer_Used": [True, False, True, False, True],
            "Irrigation_Used": [False, True, True, False, True],
            "Yield_tons_per_hectare": [4.6, 4.7, 4.6, 4.7, 4.6],
        }
    )
    joined = prepare.join_on_crop(fao, agri)
    # Potatoes n'existe pas dans le jeu synthétique, Cotton n'existe pas dans le jeu FAO
    assert joined["crop"].tolist() == ["Maize", "Rice, paddy"]
    assert joined["agri_fertilizer_rate"].tolist() == [0.5, 0.5]
