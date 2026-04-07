"""Construction des modèles et règle de sélection.

Tous les modèles apprennent le **log** du rendement (TransformedTargetRegressor) mais prédisent en t/ha :
l'API et les métriques n'ont pas à s'en soucier. exp(prédiction du log) estime le rendement médian.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["avg_temp", "rainfall_mm", "log10_pesticides_t"]
ALL_FEATURES = ["crop", *NUMERIC_FEATURES]
# Du plus simple au plus complexe : sert à départager deux modèles équivalents
COMPLEXITY_ORDER = ["baseline", "ridge", "random_forest", "hist_gb"]


class CropMedianRegressor(RegressorMixin, BaseEstimator):
    """Référence naïve : la médiane (du log) du rendement de la culture, sans regarder les conditions."""

    def fit(self, X, y):
        medians = pd.Series(np.asarray(y), index=X["crop"].to_numpy()).groupby(level=0).median()
        # Dictionnaire Python (pas de Series pandas) : le modèle se recharge sans pandas/pyarrow identiques
        self.medians_ = {str(k): float(v) for k, v in medians.items()}
        return self

    def predict(self, X):
        out = X["crop"].map(self.medians_)
        if out.isna().any():
            raise ValueError(f"Cultures inconnues : {sorted(X.loc[out.isna(), 'crop'].unique())}")
        return out.to_numpy(dtype=float)


def _regressor(name: str, params: dict, seed: int):
    if name == "ridge":
        return Ridge(**{"alpha": 1.0, **params})
    if name == "random_forest":
        # Pas de n_jobs ici : le parallélisme est déjà du côté de la recherche d'hyperparamètres
        return RandomForestRegressor(**{"n_estimators": 300, **params}, random_state=seed)
    if name == "hist_gb":
        return HistGradientBoostingRegressor(**params, random_state=seed)
    raise ValueError(f"Modèle inconnu : {name}")


def build_model(name: str, params: dict, features: list[str], seed: int = 42) -> TransformedTargetRegressor:
    """Pipeline complet : sélection des colonnes, encodage, modèle ; cible en log."""
    if name == "baseline":
        inner = CropMedianRegressor()
    else:
        numeric = [f for f in features if f in NUMERIC_FEATURES]
        transformers = []
        if "crop" in features:
            # handle_unknown="error" : une culture inconnue doit être refusée, pas prédite au hasard
            transformers.append(
                ("crop", OneHotEncoder(handle_unknown="error", sparse_output=False), ["crop"])
            )
        if numeric:
            transformers.append(("num", StandardScaler(), numeric))
        inner = Pipeline(
            [
                ("prep", ColumnTransformer(transformers, remainder="drop")),
                ("model", _regressor(name, params, seed)),
            ]
        )
    return TransformedTargetRegressor(regressor=inner, func=np.log, inverse_func=np.exp, check_inverse=False)


def select_model(fold_scores: dict[str, list[float]]) -> str:
    """Règle du PLAN : le meilleur en RMSE-log moyenne, sauf si un modèle plus simple en est à moins d'une
    erreur-type de la différence appariée (mêmes plis)."""
    scores = {k: np.asarray(v, dtype=float) for k, v in fold_scores.items()}
    best = min(scores, key=lambda k: scores[k].mean())
    for name in COMPLEXITY_ORDER:
        if name not in scores:
            continue
        if name == best:
            return best
        diff = scores[name] - scores[best]
        if diff.mean() < diff.std(ddof=1) / np.sqrt(len(diff)):
            return name
    return best
