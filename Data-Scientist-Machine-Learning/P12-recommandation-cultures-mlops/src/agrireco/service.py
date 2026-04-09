"""Ce que sert l'API : un « paquet » (modèle, références, domaine) et deux fonctions, prédire et recommander.

Le paquet est un seul fichier joblib, produit par l'étape « evaluate ». L'API ne fait que le charger.
"""

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from agrireco import recommend
from agrireco.domain import Domain


@dataclass
class Bundle:
    model: object
    reference: dict[str, float]  # rendement de référence par culture (t/ha), types Python pour le pickle
    crops: list[str]
    domain: Domain
    metadata: dict = field(default_factory=dict)


def save_bundle(bundle: Bundle, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bundle.metadata["sklearn_version"] = sklearn.__version__
    joblib.dump(bundle, path, compress=3)


def load_bundle(path: Path) -> Bundle:
    if not path.exists():
        raise FileNotFoundError(f"Modèle introuvable : {path}. Lancer `agrireco evaluate` pour le produire.")
    bundle = joblib.load(path)
    trained_with = bundle.metadata.get("sklearn_version")
    if trained_with != sklearn.__version__:
        # Un modèle picklé n'est garanti qu'avec la version de scikit-learn qui l'a produit
        raise RuntimeError(
            f"Modèle entraîné avec scikit-learn {trained_with}, version installée {sklearn.__version__}"
        )
    return bundle


def _context(avg_temp: float, rainfall_mm: float, pesticides_t: float) -> dict[str, float]:
    return {
        "avg_temp": float(avg_temp),
        "rainfall_mm": float(rainfall_mm),
        "log10_pesticides_t": float(np.log10(max(pesticides_t, 0.0) + 1)),
    }


def _frame(crops: list[str], ctx: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame({"crop": crops, **{k: [v] * len(crops) for k, v in ctx.items()}})


def predict(bundle: Bundle, crop: str, avg_temp: float, rainfall_mm: float, pesticides_t: float) -> dict:
    if crop not in bundle.crops:
        raise ValueError(f"Culture inconnue : {crop}. Cultures possibles : {bundle.crops}")
    ctx = _context(avg_temp, rainfall_mm, pesticides_t)
    y = float(bundle.model.predict(_frame([crop], ctx))[0])
    return {
        "crop": crop,
        "yield_t_ha": y,
        "relative_yield": y / float(bundle.reference[crop]),
        "out_of_range": bundle.domain.out_of_range(ctx),
        "crop_supported": bundle.domain.crop_supported(ctx, crop),
    }


def recommend_crops(bundle: Bundle, avg_temp: float, rainfall_mm: float, pesticides_t: float) -> dict:
    ctx = _context(avg_temp, rainfall_mm, pesticides_t)
    preds = pd.Series(bundle.model.predict(_frame(bundle.crops, ctx)), index=bundle.crops)
    ranking = recommend.rank(preds, pd.Series(bundle.reference))
    ranking["crop_supported"] = [bundle.domain.crop_supported(ctx, c) for c in ranking["crop"]]
    # Règle produit : une culture qu'aucun pays aux conditions proches ne pratique ne peut pas être
    # recommandée en tête (le modèle extrapole). Elle reste affichée, après les cultures appuyées.
    ranking = ranking.sort_values(
        ["crop_supported", "relative_yield"], ascending=[False, False], kind="stable"
    )
    ranking["rank"] = range(1, len(ranking) + 1)
    return {
        "ranking": ranking.reset_index(drop=True).to_dict(orient="records"),
        "out_of_range": bundle.domain.out_of_range(ctx),
    }
