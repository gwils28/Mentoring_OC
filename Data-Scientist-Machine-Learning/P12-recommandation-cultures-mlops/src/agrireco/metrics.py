"""Métriques de régression. Les rendements sont en t/ha ; la métrique principale travaille en log."""

import numpy as np
import pandas as pd


def rmse_log(y_true, y_pred) -> float:
    """RMSE du log du rendement : une erreur de 0,1 ≈ 10 % d'erreur relative, quelle que soit la culture."""
    return float(np.sqrt(np.mean((np.log(y_true) - np.log(y_pred)) ** 2)))


def r2_log(y_true, y_pred) -> float:
    lt, lp = np.log(y_true), np.log(y_pred)
    return float(1 - np.sum((lt - lp) ** 2) / np.sum((lt - np.mean(lt)) ** 2))


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def bias(y_true, y_pred) -> float:
    """Moyenne de (prédit − observé), en t/ha : négatif = le modèle sous-estime."""
    return float(np.mean(np.asarray(y_pred) - np.asarray(y_true)))


def median_relative_error(y_true, y_pred) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return float(np.median(np.abs(y_pred - y_true) / y_true))


def all_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "rmse_log": rmse_log(y_true, y_pred),
        "r2_log": r2_log(y_true, y_pred),
        "mae_t_ha": mae(y_true, y_pred),
        "median_rel_error": median_relative_error(y_true, y_pred),
        "bias_t_ha": bias(y_true, y_pred),
    }


def by_group(df: pd.DataFrame, group: str, true: str = "yield_t_ha", pred: str = "pred") -> pd.DataFrame:
    """Métriques par groupe (culture, pays…), avec l'effectif."""
    rows = [{group: g, "n": len(sub), **all_metrics(sub[true], sub[pred])} for g, sub in df.groupby(group)]
    return pd.DataFrame(rows)


def country_weighted(df: pd.DataFrame, true: str = "yield_t_ha", pred: str = "pred") -> dict[str, float]:
    """Chaque pays pèse 1 : moyenne des métriques calculées pays par pays (RMSE-log et MAE)."""
    per = by_group(df, "country", true, pred)
    return {
        "rmse_log_par_pays": float(per["rmse_log"].mean()),
        "mae_t_ha_par_pays": float(per["mae_t_ha"].mean()),
    }
