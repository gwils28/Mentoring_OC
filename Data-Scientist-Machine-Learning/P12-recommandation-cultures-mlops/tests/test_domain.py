import pandas as pd

from agrireco.domain import fit_domain


def _df():
    rows = []
    # 4 pays chauds qui cultivent l'igname, 4 pays froids qui cultivent la pomme de terre
    for i in range(4):
        rows.append((f"chaud{i}", "Yams", 26 + i * 0.5, 1500 + i * 50, 3.0 + i * 0.1))
        rows.append((f"froid{i}", "Potatoes", 6 + i * 0.5, 600 + i * 50, 4.0 + i * 0.1))
    return pd.DataFrame(rows, columns=["country", "crop", "avg_temp", "rainfall_mm", "log10_pesticides_t"])


def test_out_of_range_lists_extrapolated_conditions():
    dom = fit_domain(_df())
    ctx = {"avg_temp": 40.0, "rainfall_mm": 1000.0, "log10_pesticides_t": 3.5}
    assert dom.out_of_range(ctx) == ["avg_temp"]


def test_crop_supported_only_near_countries_that_grow_it():
    dom = fit_domain(_df())
    cold = {"avg_temp": 7.0, "rainfall_mm": 650.0, "log10_pesticides_t": 4.1}
    assert dom.crop_supported(cold, "Potatoes")
    assert not dom.crop_supported(cold, "Yams")
    assert not dom.crop_supported(cold, "Banana")  # aucune observation du tout
