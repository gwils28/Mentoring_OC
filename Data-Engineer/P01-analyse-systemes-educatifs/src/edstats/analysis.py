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
        if all(abs(corr.loc[var, other]) < threshold for other in kept):
            kept.append(var)
    return kept


def percentile_score(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Moyenne pondérée des rangs percentiles (0 = pire pays, 1 = meilleur) de chaque critère."""
    missing = set(weights) - set(df.columns)
    if missing:
        raise KeyError(f"Critères absents du dataframe : {sorted(missing)}")
    ranks = df[list(weights)].rank(pct=True)
    w = pd.Series(weights, dtype=float)
    return (ranks * w).sum(axis=1) / w.sum()


def weight_sensitivity(
    df: pd.DataFrame, criteria: list[str], n_draws: int = 1000, top: int = 10, seed: int = 0
) -> pd.Series:
    """Fréquence à laquelle chaque pays entre dans le top quand on tire les poids au hasard.

    Poids tirés selon une loi de Dirichlet (positifs, de somme 1). Un pays à 100 % est dans
    le top quels que soient les poids : la recommandation ne dépend pas d'un choix arbitraire.
    """
    rng = np.random.default_rng(seed)
    ranks = df[criteria].rank(pct=True).to_numpy()
    counts = np.zeros(len(df))
    for w in rng.dirichlet(np.ones(len(criteria)), size=n_draws):
        scores = ranks @ w
        counts[np.argsort(-scores)[:top]] += 1
    return pd.Series(counts / n_draws, index=df.index, name="frequence_top").sort_values(ascending=False)
