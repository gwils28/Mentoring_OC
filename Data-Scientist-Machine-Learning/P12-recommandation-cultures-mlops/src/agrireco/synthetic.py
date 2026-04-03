"""Analyse du jeu « Agriculture Crop Yield » (synthétique) : ACP demandée par l'énoncé et effets bruts."""

import numpy as np
import pandas as pd

ACP_VARIABLES = [
    "Rainfall_mm",
    "Temperature_Celsius",
    "Days_to_Harvest",
    "Fertilizer_Used",
    "Irrigation_Used",
]
TARGET = "Yield_tons_per_hectare"


def pca(df: pd.DataFrame, variables: list[str] = ACP_VARIABLES) -> dict:
    """ACP sur variables **toutes standardisées** (binaires comprises). Le rendement n'entre pas dans l'ACP :
    il est projeté ensuite (corrélation de chaque composante avec lui).

    Renvoie les valeurs propres (variance de chaque composante, en unités de variables standardisées),
    la part de variance expliquée, les vecteurs propres et la corrélation composantes / rendement.
    """
    x = df[variables].astype(float)
    z = (x - x.mean()) / x.std(ddof=0)
    eigval, eigvec = np.linalg.eigh(np.cov(z.to_numpy(), rowvar=False, ddof=0))
    order = np.argsort(eigval)[::-1]
    eigval, eigvec = eigval[order], eigvec[:, order]
    scores = z.to_numpy() @ eigvec
    corr_target = [float(np.corrcoef(scores[:, k], df[TARGET])[0, 1]) for k in range(len(variables))]
    return {
        "eigenvalues": eigval,
        "explained": eigval / eigval.sum(),
        "loadings": pd.DataFrame(
            eigvec, index=variables, columns=[f"CP{k + 1}" for k in range(len(variables))]
        ),
        "corr_with_target": corr_target,
    }


def raw_effects(df: pd.DataFrame) -> tuple[pd.Series, float]:
    """Régression linéaire du rendement sur toutes les variables (indicatrices pour les catégories).

    Renvoie les coefficients **bruts** (t/ha par unité : par mm, par °C, oui/non…) et le R².
    """
    X = df.drop(columns=TARGET)
    X = pd.get_dummies(X.astype({c: float for c in X.select_dtypes("bool")}), drop_first=True, dtype=float)
    X.insert(0, "constante", 1.0)
    y = df[TARGET].to_numpy()
    coef, *_ = np.linalg.lstsq(X.to_numpy(), y, rcond=None)
    pred = X.to_numpy() @ coef
    r2 = 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)
    return pd.Series(coef, index=X.columns), float(r2)


def effects_per_sd(df: pd.DataFrame, coef: pd.Series, variables: list[str] = ACP_VARIABLES) -> pd.Series:
    """Effet d'un écart-type de chaque variable (coefficient brut × écart-type), en t/ha.

    Un coefficient brut dépend de l'unité (0,005 t/ha **par mm** paraît minuscule) : pour comparer des
    variables d'unités différentes, on les ramène à leur variation typique. Pour une variable 0/1,
    l'écart-type dépend de la proportion de 1 : on lit aussi l'effet brut.
    """
    return (coef[variables] * df[variables].astype(float).std()).sort_values(ascending=False)
