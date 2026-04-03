import numpy as np
import pandas as pd
import pytest

from agrireco import synthetic


def _independent(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "Rainfall_mm": rng.uniform(100, 1000, n),
            "Temperature_Celsius": rng.uniform(15, 40, n),
            "Days_to_Harvest": rng.integers(60, 150, n),
            "Fertilizer_Used": rng.random(n) < 0.5,
            "Irrigation_Used": rng.random(n) < 0.5,
        }
    )
    df["Yield_tons_per_hectare"] = (
        0.005 * df["Rainfall_mm"] + 1.5 * df["Fertilizer_Used"] + rng.normal(0, 0.5, n)
    )
    return df


def test_independent_standardized_variables_give_flat_eigenvalues():
    res = synthetic.pca(_independent())
    assert np.allclose(res["eigenvalues"], 1.0, atol=0.1)
    assert res["explained"].sum() == pytest.approx(1.0)


def test_correlated_variables_give_a_dominant_axis():
    df = _independent()
    df["Temperature_Celsius"] = df["Rainfall_mm"] / 30 + np.random.default_rng(1).normal(0, 1, len(df))
    res = synthetic.pca(df)
    assert res["eigenvalues"][0] > 1.8


def test_raw_effects_recover_simulation_parameters():
    coef, r2 = synthetic.raw_effects(_independent())
    assert coef["Fertilizer_Used"] == pytest.approx(1.5, abs=0.05)
    assert coef["Rainfall_mm"] == pytest.approx(0.005, abs=0.0005)
    assert r2 > 0.8


def test_per_sd_effect_reveals_rainfall_hidden_by_its_unit():
    df = _independent()
    coef, _ = synthetic.raw_effects(df)
    per_sd = synthetic.effects_per_sd(df, coef)
    # 0,005 t/ha par mm × écart-type ≈ 260 mm ≈ 1,3 t/ha : plus que l'engrais (1,5 × 0,5 = 0,75)
    assert per_sd.index[0] == "Rainfall_mm"
