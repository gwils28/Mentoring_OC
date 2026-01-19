"""Tests sur de petits jeux construits à la main : on connaît la bonne réponse avant d'exécuter."""

import numpy as np
import pandas as pd
import pytest

from edstats.analysis import (
    percentile_score,
    redundant_pairs,
    select_non_redundant,
    weight_sensitivity,
)
from edstats.cleaning import find_aggregates
from edstats.quality import FilterLog, fill_rate, missing_rate


@pytest.fixture
def countries():
    return pd.DataFrame(
        {
            "Country Code": ["FRA", "WLD", "GIB", "EUU", "ARB", "NRU"],
            "Region": ["Europe & Central Asia", None, None, None, None, None],
            "2-alpha code": ["FR", "1W", "GI", "EU", "1A", "NR"],
        }
    )


def test_find_aggregates_keeps_real_territories_without_region(countries):
    # Gibraltar et Nauru n'ont pas de région mais sont de vrais territoires
    assert find_aggregates(countries) == ["ARB", "EUU", "WLD"]


def test_find_aggregates_missing_alpha2_is_not_an_aggregate():
    # sans région ET sans code alpha-2 : on ne peut pas prouver que c'est un agrégat, on le garde
    country = pd.DataFrame(
        {
            "Country Code": ["FRA", "WLD", "XXX"],
            "Region": ["Europe & Central Asia", None, None],
            "2-alpha code": ["FR", "1W", None],
        }
    )
    assert find_aggregates(country) == ["WLD"]


def test_missing_rate_is_sorted_and_in_percent():
    df = pd.DataFrame({"a": [1, None, None, None], "b": [1, 2, None, 4], "c": [1, 2, 3, 4]})
    rate = missing_rate(df)
    assert list(rate.index) == ["a", "b", "c"]
    assert rate.tolist() == [75.0, 25.0, 0.0]


def test_fill_rate_by_group():
    long = pd.DataFrame(
        {
            "indicator": ["x", "x", "y", "y"],
            "value": [1.0, np.nan, np.nan, np.nan],
        }
    )
    rate = fill_rate(long, by="indicator", value="value")
    assert rate["x"] == pytest.approx(0.5)
    assert rate["y"] == 0.0


def test_filter_log_records_rows_before_and_after():
    log = FilterLog()
    df = pd.DataFrame({"v": range(10)})
    kept = log.apply(df, df["v"] < 4, "garder v < 4")
    assert len(kept) == 4
    row = log.to_frame().iloc[0]
    assert (row["lignes_avant"], row["lignes_apres"], row["lignes_supprimees"]) == (10, 4, 6)


def test_redundant_pairs_uses_absolute_value_and_ignores_diagonal():
    corr = pd.DataFrame(
        [[1.0, -0.9, 0.2], [-0.9, 1.0, 0.1], [0.2, 0.1, 1.0]],
        index=list("abc"),
        columns=list("abc"),
    )
    pairs = redundant_pairs(corr, threshold=0.7)
    assert len(pairs) == 1
    assert set(pairs.iloc[0][["var_1", "var_2"]]) == {"a", "b"}


def test_redundant_pairs_on_corr_of_a_pivot_table():
    # après pivot_table, index et colonnes de .corr() portent le même nom
    wide = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 4, 6, 9], "c": [4, 1, 3, 2]})
    wide.columns.name = "Indicator Code"
    pairs = redundant_pairs(wide.corr(), threshold=0.7)
    assert list(pairs.columns) == ["var_1", "var_2", "correlation"]
    assert set(pairs.iloc[0][["var_1", "var_2"]]) == {"a", "b"}


def test_percentile_score_ranks_and_weights():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [30, 20, 10]}, index=["P1", "P2", "P3"])
    # a seul compte : P3 a le meilleur rang
    score = percentile_score(df, {"a": 1.0, "b": 0.0})
    assert score.idxmax() == "P3"
    # poids égaux : a et b s'opposent, tous les pays sont à égalité
    score = percentile_score(df, {"a": 0.5, "b": 0.5})
    # égalité à la précision flottante près (0.5·r_a + 0.5·r_b n'est pas exactement constant)
    assert np.allclose(score, score.iloc[0])


def test_percentile_score_rejects_unknown_columns():
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(KeyError):
        percentile_score(df, {"inconnu": 1.0})


def test_weight_sensitivity_is_reproducible_and_bounded():
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.random((30, 3)), columns=list("abc"))
    freq_1 = weight_sensitivity(df, list("abc"), n_draws=200, top=5, seed=42)
    freq_2 = weight_sensitivity(df, list("abc"), n_draws=200, top=5, seed=42)
    pd.testing.assert_series_equal(freq_1, freq_2)
    assert freq_1.between(0, 1).all()
    # chaque tirage place exactement 5 pays dans le top
    assert freq_1.sum() == pytest.approx(5)


def test_select_non_redundant_follows_business_priority():
    corr = pd.DataFrame(
        [[1.0, 0.9, 0.1], [0.9, 1.0, 0.2], [0.1, 0.2, 1.0]],
        index=list("abc"),
        columns=list("abc"),
    )
    # b passe avant a : c'est b qu'on garde dans la paire redondante (a, b)
    assert select_non_redundant(corr, priority=["b", "a", "c"], threshold=0.7) == ["b", "c"]
    assert select_non_redundant(corr, priority=["a", "b", "c"], threshold=0.7) == ["a", "c"]


def test_select_non_redundant_requires_full_priority():
    corr = pd.DataFrame([[1.0, 0.1], [0.1, 1.0]], index=list("ab"), columns=list("ab"))
    with pytest.raises(ValueError):
        select_non_redundant(corr, priority=["a"], threshold=0.7)


def test_select_non_redundant_rejects_nan_correlation_with_kept_variable():
    # c est constante : sa corrélation avec a est NaN, on ne doit pas l'écarter en silence
    corr = pd.DataFrame(
        [[1.0, 0.1, np.nan], [0.1, 1.0, np.nan], [np.nan, np.nan, 1.0]],
        index=list("abc"),
        columns=list("abc"),
    )
    with pytest.raises(ValueError, match="c"):
        select_non_redundant(corr, priority=["a", "b", "c"], threshold=0.7)


# --- percentile_score : NaN et poids ---


def test_percentile_score_rejects_nan_in_criteria():
    df = pd.DataFrame({"a": [1, np.nan, 3], "b": [1.0, 2.0, 3.0]}, index=["P1", "P2", "P3"])
    with pytest.raises(ValueError, match=r"a.*1"):
        percentile_score(df, {"a": 0.5, "b": 0.5})


def test_percentile_score_ignores_nan_in_unused_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "autre": [np.nan, 1, 2]})
    assert percentile_score(df, {"a": 1.0}).notna().all()


@pytest.mark.parametrize("weights", [{"a": -1.0, "b": 2.0}, {"a": 0.0, "b": 0.0}])
def test_percentile_score_rejects_negative_or_zero_sum_weights(weights):
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    with pytest.raises(ValueError):
        percentile_score(df, weights)


# --- weight_sensitivity : NaN et tirage autour des poids métier ---


def test_weight_sensitivity_rejects_nan_in_criteria():
    df = pd.DataFrame({"a": [1, np.nan, 3], "b": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="a"):
        weight_sensitivity(df, ["a", "b"], n_draws=10, top=1)


def test_weight_sensitivity_centered_on_business_weights():
    # P1 gagne si a domine, P2 si b domine. Avec des poids centrés sur a (0.9) et une forte
    # concentration, P1 est presque toujours dans le top 1 ; en tirage uniforme, environ une fois sur deux.
    df = pd.DataFrame({"a": [3, 1, 2], "b": [1, 3, 2]}, index=["P1", "P2", "P3"])
    centered = weight_sensitivity(
        df, ["a", "b"], n_draws=500, top=1, seed=0, center={"a": 0.9, "b": 0.1}, concentration=200
    )
    uniform = weight_sensitivity(df, ["a", "b"], n_draws=500, top=1, seed=0)
    assert centered["P1"] > 0.95
    assert 0.3 < uniform["P1"] < 0.7


def test_weight_sensitivity_center_must_match_criteria():
    df = pd.DataFrame({"a": [1, 2], "b": [2, 1]})
    with pytest.raises(ValueError):
        weight_sensitivity(df, ["a", "b"], n_draws=10, top=1, center={"a": 1.0})
