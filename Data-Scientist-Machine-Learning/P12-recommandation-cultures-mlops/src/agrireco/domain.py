"""Domaine de validité : signaler quand on demande au modèle de parler de ce qu'il n'a jamais vu.

Deux signaux :
- une condition sort de la plage observée à l'entraînement (extrapolation) ;
- une culture n'est cultivée par **aucun pays aux conditions proches** dans les données : sa prédiction n'est
  appuyée par aucune observation comparable (ex. l'igname dans un climat tempéré).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from agrireco.modeling import NUMERIC_FEATURES


@dataclass
class Domain:
    ranges: dict[str, tuple[float, float]]
    center: np.ndarray
    scale: np.ndarray
    # Profil moyen (conditions standardisées) de chaque pays, et cultures qu'il pratique. Types Python et
    # numpy seulement : le domaine est picklé avec le modèle et doit se recharger sans pandas ni pyarrow.
    countries: list[str]
    country_profiles: np.ndarray
    country_crops: dict[str, list[str]]
    threshold: float

    def out_of_range(self, context: dict[str, float]) -> list[str]:
        return [f for f, (lo, hi) in self.ranges.items() if not lo <= context[f] <= hi]

    def nearest_distance(self, context: dict[str, float], crop: str) -> float:
        x = (np.array([context[f] for f in NUMERIC_FEATURES]) - self.center) / self.scale
        rows = [i for i, c in enumerate(self.countries) if crop in self.country_crops[c]]
        if not rows:
            return float("inf")
        return float(np.min(np.linalg.norm(self.country_profiles[rows] - x, axis=1)))

    def crop_supported(self, context: dict[str, float], crop: str) -> bool:
        return self.nearest_distance(context, crop) <= self.threshold


def fit_domain(df: pd.DataFrame, quantile: float = 0.95) -> Domain:
    """Construit le domaine à partir des données d'entraînement.

    Seuil : quantile `quantile` des distances de chaque pays à son plus proche voisin (autre pays). Une
    culture est « appuyée » si un pays qui la cultive est au plus à cette distance des conditions demandées.
    """
    ranges = {f: (float(df[f].min()), float(df[f].max())) for f in NUMERIC_FEATURES}
    profiles = df.groupby("country")[NUMERIC_FEATURES].mean()
    center, scale = profiles.mean().to_numpy(), profiles.std(ddof=0).to_numpy()
    z = (profiles - center) / scale
    d = np.linalg.norm(z.to_numpy()[:, None, :] - z.to_numpy()[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    threshold = float(np.quantile(d.min(axis=1), quantile))
    crops = {str(c): [str(x) for x in sorted(v)] for c, v in df.groupby("country")["crop"].unique().items()}
    names = [str(c) for c in z.index]
    return Domain(ranges, center, scale, names, z.to_numpy(dtype=float), crops, threshold)
