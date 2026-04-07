"""Tests du rendement relatif, du classement et de l'évaluation de la recommandation."""

import numpy as np
import pandas as pd
import pytest

from agrireco import recommend


def test_reference_is_median_of_country_medians():
    # Le pays A a 3 années à 10 t/ha, le pays B une seule à 2 t/ha, le pays C une à 4 t/ha.
    # Médiane des lignes = 10 ; médiane des médianes par pays = 4 : les séries longues ne pèsent pas plus.
    df = pd.DataFrame(
        {
            "country": ["A", "A", "A", "B", "C"],
            "crop": ["Maize"] * 5,
            "yield_t_ha": [10.0, 10.0, 10.0, 2.0, 4.0],
        }
    )
    ref = recommend.reference_yields(df)
    assert ref["Maize"] == pytest.approx(4.0)
    assert recommend.reference_yields(df, by_country=False)["Maize"] == pytest.approx(10.0)


def test_rank_sorts_by_relative_yield_not_raw_tonnes():
    pred = pd.Series({"Potatoes": 16.0, "Soybeans": 2.4})
    ref = pd.Series({"Potatoes": 16.0, "Soybeans": 1.6})
    ranking = recommend.rank(pred, ref)
    assert ranking["crop"].tolist() == ["Soybeans", "Potatoes"]
    assert ranking["relative_yield"].tolist() == pytest.approx([1.5, 1.0])
    assert ranking["rank"].tolist() == [1, 2]


def _eval_table():
    # 2 pays × 1 année ; dans chaque groupe, 3 cultures observées
    return pd.DataFrame(
        {
            "country": ["A"] * 3 + ["B"] * 3,
            "year": [2000] * 6,
            "crop": ["Maize", "Potatoes", "Soybeans"] * 2,
            "rel_obs": [1.2, 0.8, 1.0, 0.9, 1.1, 1.0],
            "rel_pred": [1.3, 0.7, 1.0, 1.2, 1.0, 0.9],
        }
    )


def test_top1_and_gain_per_group():
    groups = recommend.evaluate_groups(_eval_table(), score="rel_pred")
    a = groups.set_index("country").loc["A"]
    b = groups.set_index("country").loc["B"]
    assert a["top1_ok"] and not b["top1_ok"]  # B : le modèle choisit Maize, le meilleur observé est Potatoes
    assert a["gain"] == pytest.approx(1.2 - 1.0)
    assert b["gain"] == pytest.approx(0.9 - 1.0)
    assert a["oracle_gain"] == pytest.approx(0.2)
    assert a["k"] == 3 and a["chance"] == pytest.approx(1 / 3)


def test_groups_with_fewer_than_min_crops_are_excluded():
    df = _eval_table().iloc[:5]  # B n'a plus que 2 cultures
    groups = recommend.evaluate_groups(df, score="rel_pred", min_crops=3)
    assert groups["country"].tolist() == ["A"]


def test_constant_ranking_ignores_conditions():
    train = pd.DataFrame(
        {
            "country": ["A", "A", "B", "B"],
            "year": [2000] * 4,
            "crop": ["Maize", "Soybeans", "Maize", "Soybeans"],
            "rel_obs": [1.5, 1.0, 1.4, 0.9],
        }
    )
    order = recommend.constant_order(train)
    assert order.tolist() == ["Maize", "Soybeans"]
    scores = recommend.constant_scores(pd.Series(["Soybeans", "Maize", "Yams"]), order)
    # Maize doit passer devant Soybeans ; une culture absente de l'entraînement passe en dernier
    assert scores.iloc[1] > scores.iloc[0] > scores.iloc[2]


def test_paired_country_bootstrap_is_reproducible_and_paired():
    groups = pd.DataFrame(
        {
            "country": list("ABCDEFGH"),
            "model": [1, 1, 0, 1, 1, 0, 1, 1],
            "reference": [0, 1, 0, 0, 1, 0, 0, 1],
        }
    )
    ci1 = recommend.bootstrap_by_country(
        groups, lambda g: (g["model"] - g["reference"]).mean(), n=500, seed=0
    )
    ci2 = recommend.bootstrap_by_country(
        groups, lambda g: (g["model"] - g["reference"]).mean(), n=500, seed=0
    )
    assert ci1 == ci2
    low, high = ci1
    assert low <= 3 / 8 <= high


def test_kendall_per_country_handles_ties():
    df = pd.DataFrame(
        {
            "country": ["A"] * 3,
            "year": [2000] * 3,
            "crop": ["x", "y", "z"],
            "rel_obs": [1.0, 2.0, 3.0],
            "rel_pred": [1.0, 1.0, 1.0],  # que des ex æquo : tau non défini, groupe ignoré
        }
    )
    assert np.isnan(recommend.kendall_by_country(df, "rel_pred"))
