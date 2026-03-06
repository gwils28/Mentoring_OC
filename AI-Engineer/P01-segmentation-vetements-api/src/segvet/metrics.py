"""Mesurer une segmentation : matrice de confusion, IoU, Dice."""

import numpy as np

from segvet.labels import N_CLASSES


def confusion_matrix(truth: np.ndarray, pred: np.ndarray, n_classes: int = N_CLASSES) -> np.ndarray:
    """Matrice (vérité × prédiction) : case [i, j] = nombre de pixels de classe i prédits en classe j."""
    if truth.shape != pred.shape:
        raise ValueError(f"Tailles différentes : vérité {truth.shape}, prédiction {pred.shape}")
    # Un identifiant hors de 0..n_classes-1 (ex. 255 = « ignoré ») fausserait en silence une autre case
    for name, labels in (("vérité", truth), ("prédiction", pred)):
        outside = (labels < 0) | (labels >= n_classes)
        if outside.any():
            raise ValueError(
                f"{name} : {int(outside.sum())} pixel(s) hors des classes 0 à {n_classes - 1} "
                f"(valeurs {np.unique(labels[outside]).tolist()})"
            )
    index = truth.astype(np.int64).ravel() * n_classes + pred.astype(np.int64).ravel()
    return np.bincount(index, minlength=n_classes**2).reshape(n_classes, n_classes)


def iou_per_class(cm: np.ndarray) -> np.ndarray:
    """IoU = intersection / union par classe ; NaN si absente de la vérité comme de la prédiction."""
    intersection = np.diag(cm).astype(float)
    union = cm.sum(axis=0) + cm.sum(axis=1) - intersection
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(union > 0, intersection / union, np.nan)


def dice_per_class(cm: np.ndarray) -> np.ndarray:
    """Dice = 2 × intersection / (pixels vrais + pixels prédits), c'est-à-dire le F1 au niveau pixel."""
    intersection = np.diag(cm).astype(float)
    total = cm.sum(axis=0) + cm.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(total > 0, 2 * intersection / total, np.nan)


def pixel_accuracy(cm: np.ndarray) -> float:
    """Part des pixels bien classés : trompeuse quand le fond domine."""
    return float(np.trace(cm) / cm.sum())


def merge_classes(cm: np.ndarray, groups: list[list[int]]) -> np.ndarray:
    """Fusionne des classes (ex. chaussures gauche + droite) : un groupe = une ligne et une colonne."""
    covered = sorted(i for group in groups for i in group)
    if covered != list(range(cm.shape[0])):
        raise ValueError("Chaque classe doit appartenir à exactement un groupe")
    projection = np.zeros((cm.shape[0], len(groups)), dtype=cm.dtype)
    for g, group in enumerate(groups):
        projection[group, g] = 1
    return projection.T @ cm @ projection
