"""Évaluation du PLAN.md : vue fusionnée, mIoU vêtements, intervalle bootstrap, règle de décision."""

import numpy as np
import pandas as pd

from segvet.labels import CLASS_TO_ID
from segvet.metrics import confusion_matrix, dice_per_class, iou_per_class, merge_classes

# Vue fusionnée : gauche et droite réunies (on somme les lignes et colonnes de la matrice de confusion)
FUSED = {
    "Fond": ["Background"],
    "Chapeau": ["Hat"],
    "Cheveux": ["Hair"],
    "Lunettes": ["Sunglasses"],
    "Haut": ["Upper-clothes"],
    "Jupe": ["Skirt"],
    "Pantalon": ["Pants"],
    "Robe": ["Dress"],
    "Ceinture": ["Belt"],
    "Chaussures": ["Left-shoe", "Right-shoe"],
    "Visage": ["Face"],
    "Jambes": ["Left-leg", "Right-leg"],
    "Bras": ["Left-arm", "Right-arm"],
    "Sac": ["Bag"],
    "Écharpe": ["Scarf"],
}
FUSED_NAMES = list(FUSED)
FUSED_GROUPS = [[CLASS_TO_ID[c] for c in classes] for classes in FUSED.values()]

# Métrique principale : familles de vêtements présentes dans au moins 5 images (écharpe, 3 images, à part)
CLOTHING = ["Chapeau", "Lunettes", "Haut", "Jupe", "Pantalon", "Robe", "Ceinture", "Chaussures", "Sac"]
# Règle de décision fixée avant les résultats (PLAN.md)
KEY_GARMENTS = ["Haut", "Pantalon", "Robe", "Jupe", "Chaussures"]
CI_FLOOR, KEY_FLOOR = 0.60, 0.50


def image_confusions(truths: list[np.ndarray], preds: list[np.ndarray]) -> np.ndarray:
    """Une matrice de confusion 18 × 18 par image, empilées : forme (n_images, 18, 18)."""
    return np.stack([confusion_matrix(t, p) for t, p in zip(truths, preds, strict=True)])


def fuse(cm: np.ndarray) -> np.ndarray:
    return merge_classes(cm, FUSED_GROUPS)


def clothing_miou(cm18: np.ndarray) -> float:
    """mIoU vêtements (métrique principale) à partir d'une matrice 18 × 18 cumulée."""
    iou = pd.Series(iou_per_class(fuse(cm18)), index=FUSED_NAMES)
    return float(iou[CLOTHING].mean())  # NaN (classe absente partout) exclu, comme prévu au plan


def per_class_table(cms: np.ndarray) -> pd.DataFrame:
    """IoU et Dice par famille (vue fusionnée), avec le nombre d'images où la famille est annotée."""
    fused = np.stack([fuse(cm) for cm in cms])
    total = fused.sum(axis=0)
    return pd.DataFrame(
        {
            "iou": iou_per_class(total),
            "dice": dice_per_class(total),
            "images": (fused.sum(axis=2) > 0).sum(axis=0),
            "pixels_annotes": total.sum(axis=1),
        },
        index=pd.Index(FUSED_NAMES, name="famille"),
    )


def per_image_clothing_miou(cms: np.ndarray) -> np.ndarray:
    """Diagnostic : mIoU vêtements de chaque image (classes présentes dans la vérité ou la prédiction)."""
    return np.array([clothing_miou(cm) for cm in cms])


def bootstrap(cms: np.ndarray, n_boot: int = 2000, seed: int = 0, others: np.ndarray | None = None) -> dict:
    """Intervalle percentile à 95 % du mIoU vêtements en tirant les images avec remise.

    Si `others` (mêmes images, autre variante d'envoi) est fourni, on calcule aussi la différence
    appariée : les deux variantes sont recalculées sur le même tirage d'images.
    """
    rng = np.random.default_rng(seed)
    n = len(cms)
    names = pd.Index(FUSED_NAMES)
    clothing_idx = names.get_indexer(CLOTHING)
    estimates, deltas, degenerate = [], [], 0
    for _ in range(n_boot):
        sample = rng.integers(0, n, n)
        total = cms[sample].sum(axis=0)
        truth_pixels = fuse(total).sum(axis=1)[clothing_idx]
        degenerate += bool((truth_pixels == 0).any())
        estimates.append(clothing_miou(total))
        if others is not None:
            deltas.append(estimates[-1] - clothing_miou(others[sample].sum(axis=0)))
    result = {
        "estimate": clothing_miou(cms.sum(axis=0)),
        "ci": tuple(np.percentile(estimates, [2.5, 97.5])),
        "degenerate_share": degenerate / n_boot,
    }
    if others is not None:
        result["delta"] = result["estimate"] - clothing_miou(others.sum(axis=0))
        result["delta_ci"] = tuple(np.percentile(deltas, [2.5, 97.5]))
    return result


def decision(ci_low: float, table: pd.DataFrame) -> tuple[str, list[str]]:
    """Applique la règle du plan. Renvoie le verdict et la liste des vêtements clés sous le seuil."""
    weak = [g for g in KEY_GARMENTS if not table.loc[g, "iou"] >= KEY_FLOOR]
    if ci_low >= CI_FLOOR and not weak:
        return "non disqualifié pour un pilote", weak
    return "insuffisant", weak
