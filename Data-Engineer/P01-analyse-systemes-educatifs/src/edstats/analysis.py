"""Analyse univariée, redondance et score de potentiel pays."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from edstats import viz


def describe_and_plot(
    values: pd.Series, title: str, xlabel: str, log_scale: bool = False, save_as: str | None = None
) -> pd.Series:
    """Statistiques descriptives + histogramme d'un indicateur (une ligne = un pays).

    La moyenne (tirets) et la médiane (trait plein) sont tracées : leur écart se lit
    directement comme l'asymétrie de la distribution.
    """
    stats = values.describe()
    stats["asymetrie"] = values.skew()
    fig, ax = plt.subplots(figsize=(8, 3.8))
    sns.histplot(values.dropna(), bins=30, log_scale=log_scale, color=viz.BLUE, edgecolor=viz.SURFACE, ax=ax)
    ax.axvline(
        stats["mean"], color=viz.TEXT, linestyle="--", linewidth=1.5, label=f"moyenne = {stats['mean']:,.1f}"
    )
    ax.axvline(stats["50%"], color=viz.ORANGE, linewidth=2, label=f"médiane = {stats['50%']:,.1f}")
    ax.set(title=title, xlabel=xlabel, ylabel="Nombre de pays")
    ax.legend(loc="upper right")
    if save_as:
        viz.save(fig, save_as)
    plt.show()
    return stats


def redundant_pairs(corr: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
    """Paires de variables dont |corrélation| ≥ seuil (chaque paire une seule fois)."""
    upper = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1))
    # index et colonnes d'une corr() issue d'un pivot portent le même nom : on les renomme
    upper = upper.rename_axis(index="var_1", columns="var_2")
    pairs = upper.stack().rename("correlation").reset_index()
    pairs = pairs[pairs["correlation"].abs() >= threshold]
    return pairs.sort_values("correlation", key=abs, ascending=False, ignore_index=True)


def select_non_redundant(corr: pd.DataFrame, priority: list[str], threshold: float = 0.7) -> list[str]:
    """Parcourt les variables par ordre d'importance métier et garde chacune seulement
    si elle n'est pas corrélée (|r| ≥ seuil) à une variable déjà gardée."""
    if set(priority) != set(corr.columns):
        raise ValueError("La liste de priorité doit contenir exactement les colonnes de la matrice.")
    kept: list[str] = []
    for var in priority:
        # une corrélation NaN (variable constante, aucun pays en commun…) ferait échouer « < seuil »
        # et écarterait la variable sans le dire : on préfère s'arrêter et nommer le problème
        undefined = [other for other in kept if pd.isna(corr.loc[var, other])]
        if undefined:
            raise ValueError(
                f"Corrélation non définie (NaN) entre « {var} » et {undefined} : impossible de juger."
            )
        if all(abs(corr.loc[var, other]) < threshold for other in kept):
            kept.append(var)
    return kept


def _check_no_nan(df: pd.DataFrame, criteria: list[str]) -> None:
    """Un rang de NaN vaut NaN et fausse le score : on exige des critères complets."""
    nan_counts = df[criteria].isna().sum()
    nan_counts = nan_counts[nan_counts > 0]
    if not nan_counts.empty:
        detail = ", ".join(f"{col} : {n} NaN" for col, n in nan_counts.items())
        raise ValueError(f"Critères incomplets ({detail}). Filtrer ou imputer ces pays avant le score.")


def percentile_score(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Moyenne pondérée des rangs percentiles (0 = pire pays, 1 = meilleur) de chaque critère."""
    missing = set(weights) - set(df.columns)
    if missing:
        raise KeyError(f"Critères absents du dataframe : {sorted(missing)}")
    w = pd.Series(weights, dtype=float)
    if (w < 0).any() or w.sum() == 0:
        raise ValueError(f"Les poids doivent être positifs ou nuls, de somme non nulle : {weights}")
    _check_no_nan(df, list(weights))
    ranks = df[list(weights)].rank(pct=True)
    return (ranks * w).sum(axis=1) / w.sum()


def weight_sensitivity(
    df: pd.DataFrame,
    criteria: list[str],
    n_draws: int = 1000,
    top: int = 10,
    seed: int = 0,
    center: dict[str, float] | None = None,
    concentration: float | None = None,
) -> pd.Series:
    """Fréquence à laquelle chaque pays entre dans le top quand on tire les poids au hasard.

    Les poids sont tirés selon une loi de Dirichlet (positifs, de somme 1). Deux questions différentes :

    - sans ``center`` : Dirichlet(1, …, 1), tirage **uniforme sur le simplexe**. Toutes les pondérations
      se valent, même les plus extrêmes (un seul critère presque seul). Question posée : « la
      recommandation tient-elle quels que soient les poids ? ». Un pays à 100 % est dans le top
      quelles que soient les priorités.
    - avec ``center`` (les poids métier) : Dirichlet(concentration × poids normalisés), tirage
      **autour des poids métier**. Plus ``concentration`` est grande (100 par défaut), plus les poids
      tirés restent proches du centre. Question posée : « une petite erreur sur nos poids change-t-elle
      le classement ? ».
    """
    _check_no_nan(df, criteria)
    if center is None:
        alpha = np.ones(len(criteria))
    else:
        if set(center) != set(criteria):
            raise ValueError(
                f"center doit donner un poids à chaque critère {criteria} : reçu {sorted(center)}"
            )
        w = np.array([center[c] for c in criteria], dtype=float)
        if (w <= 0).any():
            # Dirichlet exige des paramètres strictement positifs
            raise ValueError(f"Les poids centraux doivent être strictement positifs : {center}")
        alpha = (100.0 if concentration is None else concentration) * w / w.sum()
    rng = np.random.default_rng(seed)
    ranks = df[criteria].rank(pct=True).to_numpy()
    counts = np.zeros(len(df))
    for w in rng.dirichlet(alpha, size=n_draws):
        scores = ranks @ w
        counts[np.argsort(-scores)[:top]] += 1
    return pd.Series(counts / n_draws, index=df.index, name="frequence_top").sort_values(ascending=False)
