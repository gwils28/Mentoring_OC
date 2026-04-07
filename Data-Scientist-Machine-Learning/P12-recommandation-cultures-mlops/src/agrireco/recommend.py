"""Recommandation : classer les cultures par rendement relatif, et évaluer ce classement.

Rendement relatif = rendement ÷ rendement de référence de la culture (médiane des médianes par pays).
« 1,3 » se lit : 30 % au-dessus de ce qu'on obtient d'habitude pour cette culture.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd
from scipy.stats import kendalltau


def reference_yields(df: pd.DataFrame, by_country: bool = True) -> pd.Series:
    """Rendement de référence par culture. `by_country=True` : médiane des médianes par pays."""
    if by_country:
        return df.groupby(["crop", "country"])["yield_t_ha"].median().groupby("crop").median()
    return df.groupby("crop")["yield_t_ha"].median()


def rank(predicted: pd.Series, reference: pd.Series) -> pd.DataFrame:
    """Classement des cultures (index de `predicted`) par rendement relatif décroissant."""
    out = pd.DataFrame({"crop": predicted.index, "yield_t_ha": predicted.to_numpy()})
    out["relative_yield"] = out["yield_t_ha"] / out["crop"].map(reference).to_numpy()
    out = out.sort_values("relative_yield", ascending=False, kind="stable").reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out


def evaluate_groups(df: pd.DataFrame, score: str, min_crops: int = 3) -> pd.DataFrame:
    """Une ligne par (pays, année) ayant au moins `min_crops` cultures observées.

    `df` contient rel_obs (rendement relatif observé) et `score` (le score qui classe les cultures).
    top1_ok : la culture classée 1ʳᵉ est celle au meilleur rendement relatif observé.
    gain : rel_obs de la culture recommandée − moyenne des rel_obs du groupe ;
    oracle_gain : le maximum possible.
    """
    rows = []
    for (country, year), g in df.groupby(["country", "year"]):
        if len(g) < min_crops:
            continue
        chosen = g.loc[g[score].idxmax()]
        best = g.loc[g["rel_obs"].idxmax()]
        mean_obs = g["rel_obs"].mean()
        rows.append(
            {
                "country": country,
                "year": year,
                "k": len(g),
                "chance": 1 / len(g),
                "recommended": chosen["crop"],
                "top1_ok": bool(chosen["crop"] == best["crop"]),
                "gain": chosen["rel_obs"] - mean_obs,
                "oracle_gain": best["rel_obs"] - mean_obs,
            }
        )
    return pd.DataFrame(rows)


def constant_order(train: pd.DataFrame) -> pd.Index:
    """Référence « classement constant » : cultures triées par rang moyen de rendement relatif observé
    dans les groupes (pays, année) de l'entraînement ; le même ordre quelles que soient les conditions."""
    ranks = train.groupby(["country", "year"])["rel_obs"].rank(ascending=False)
    return train.assign(r=ranks).groupby("crop")["r"].mean().sort_values(kind="stable").index


def constant_scores(crops: pd.Series, order: pd.Index) -> pd.Series:
    """Score décroissant selon la position dans `order` ; une culture absente passe en dernier."""
    position = {c: i for i, c in enumerate(order)}
    return crops.map(lambda c: -position.get(c, len(order))).astype(float)


def kendall_by_country(df: pd.DataFrame, score: str, min_crops: int = 3) -> float:
    """Tau-b de Kendall entre classement prédit et observé, moyenné par pays puis entre pays.

    Groupes où le tau n'est pas défini (que des ex æquo) ignorés ; NaN si aucun groupe n'est défini.
    """
    per_group = []
    for (country, _), g in df.groupby(["country", "year"]):
        if len(g) < min_crops:
            continue
        tau = kendalltau(g[score], g["rel_obs"]).statistic
        if not np.isnan(tau):
            per_group.append((country, tau))
    if not per_group:
        return float("nan")
    return float(pd.DataFrame(per_group, columns=["country", "tau"]).groupby("country")["tau"].mean().mean())


def bootstrap_by_country(
    groups: pd.DataFrame, statistic: Callable[[pd.DataFrame], float], n: int = 2000, seed: int = 0
) -> tuple[float, float]:
    """Intervalle percentile à 95 % en tirant des **pays** avec remise (toutes leurs lignes suivent).

    Passer une statistique qui compare deux colonnes de la même ligne donne un bootstrap apparié.
    """
    rng = np.random.default_rng(seed)
    by_country = {c: g for c, g in groups.groupby("country")}
    countries = np.array(list(by_country))
    stats = []
    for _ in range(n):
        sample = rng.choice(countries, size=len(countries), replace=True)
        stats.append(statistic(pd.concat([by_country[c] for c in sample], ignore_index=True)))
    low, high = np.percentile(stats, [2.5, 97.5])
    return float(low), float(high)
