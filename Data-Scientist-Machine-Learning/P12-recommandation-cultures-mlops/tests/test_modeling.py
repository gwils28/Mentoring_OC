"""Tests des briques de modélisation sur des tables construites à la main."""

import numpy as np
import pandas as pd
import pytest

from agrireco import metrics, modeling, split


def _toy(n_countries=10, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_countries):
        temp, rain, pest = rng.uniform(5, 28), rng.uniform(300, 2500), rng.uniform(10, 1e5)
        for crop, base in [("Maize", 3.0), ("Potatoes", 16.0), ("Soybeans", 1.6)]:
            for year in (2000, 2001):
                y = base * np.exp(0.02 * (temp - 15) + rng.normal(0, 0.1))
                rows.append((f"C{c}", crop, year, y, rain, pest, temp))
    df = pd.DataFrame(
        rows, columns=["country", "crop", "year", "yield_t_ha", "rainfall_mm", "pesticides_t", "avg_temp"]
    )
    return df.assign(log10_pesticides_t=np.log10(df["pesticides_t"] + 1))


def test_group_split_never_shares_a_country():
    df = _toy(20)
    train, test = split.group_test_split(df, test_size=0.2, seed=42)
    assert set(train["country"]).isdisjoint(test["country"])
    assert len(train) + len(test) == len(df)
    assert test["country"].nunique() == 4


def test_group_split_is_reproducible():
    df = _toy(20)
    a = split.group_test_split(df, 0.2, 42)[1]["country"].unique()
    b = split.group_test_split(df, 0.2, 42)[1]["country"].unique()
    assert list(a) == list(b)


def test_metrics_on_known_values():
    y = np.array([1.0, 10.0])
    p = np.array([2.0, 10.0])
    assert metrics.rmse_log(y, p) == pytest.approx(np.sqrt(np.log(2) ** 2 / 2))
    assert metrics.mae(y, p) == pytest.approx(0.5)
    assert metrics.bias(y, p) == pytest.approx(0.5)
    assert metrics.median_relative_error(y, p) == pytest.approx(0.5)


def test_crop_median_baseline_ignores_conditions():
    df = _toy(5)
    model = modeling.build_model("baseline", {}, features=modeling.ALL_FEATURES)
    model.fit(df, df["yield_t_ha"])
    pred = model.predict(df)
    potatoes = df["crop"] == "Potatoes"
    assert np.unique(pred[potatoes]).size == 1
    assert pred[potatoes][0] == pytest.approx(np.exp(np.median(np.log(df.loc[potatoes, "yield_t_ha"]))))


# Jeu minuscule (48 lignes) : on autorise des feuilles de 2 lignes, sinon le boosting ne coupe pas
@pytest.mark.parametrize(
    "name, params", [("ridge", {}), ("random_forest", {}), ("hist_gb", {"min_samples_leaf": 2})]
)
def test_models_predict_positive_yields_in_t_ha(name, params):
    df = _toy(8)
    model = modeling.build_model(name, params, features=modeling.ALL_FEATURES, seed=0)
    model.fit(df, df["yield_t_ha"])
    pred = model.predict(df)
    assert (pred > 0).all()
    # Ordre de grandeur respecté : la pomme de terre reste au-dessus du soja
    assert pred[df["crop"] == "Potatoes"].mean() > 5 * pred[df["crop"] == "Soybeans"].mean()


def test_unknown_crop_is_refused_at_prediction():
    df = _toy(5)
    model = modeling.build_model("ridge", {}, features=modeling.ALL_FEATURES).fit(df, df["yield_t_ha"])
    bad = df.head(1).assign(crop="Banana")
    with pytest.raises(ValueError):
        model.predict(bad)


def test_feature_subset_only_uses_listed_columns():
    df = _toy(5)
    model = modeling.build_model("ridge", {}, features=["crop"]).fit(df, df["yield_t_ha"])
    shuffled = df.assign(avg_temp=df["avg_temp"].sample(frac=1, random_state=0).to_numpy())
    np.testing.assert_allclose(model.predict(df), model.predict(shuffled))


def test_selection_keeps_simpler_model_within_one_standard_error():
    # RF est meilleur en moyenne, mais de moins d'une erreur-type : on garde Ridge (plus simple)
    folds = {
        "baseline": [0.90, 0.95, 0.85, 0.92, 0.88],
        "ridge": [0.60, 0.75, 0.55, 0.68, 0.62],
        "random_forest": [0.61, 0.62, 0.60, 0.64, 0.62],
    }
    assert modeling.select_model(folds) == "ridge"


def test_selection_takes_best_when_clearly_better():
    folds = {
        "ridge": [0.70, 0.71, 0.69, 0.72, 0.70],
        "hist_gb": [0.60, 0.61, 0.59, 0.62, 0.60],
    }
    assert modeling.select_model(folds) == "hist_gb"
