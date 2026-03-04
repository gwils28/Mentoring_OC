"""Transformer la réponse de l'API (un masque base64 par classe) en une carte de classes par pixel."""

import base64
import io

import numpy as np
from PIL import Image

from segvet.labels import CLASS_TO_ID


def decode_base64_mask(b64: str, size: tuple[int, int]) -> np.ndarray:
    """Décode un masque PNG encodé en base64 et le ramène à `size` = (largeur, hauteur).

    Renvoie un tableau booléen : True là où la classe est présente. Le redimensionnement se fait au plus
    proche voisin (NEAREST) : une interpolation lisse inventerait des valeurs intermédiaires.
    """
    mask = Image.open(io.BytesIO(base64.b64decode(b64)))
    if mask.mode != "L":
        mask = mask.convert("L")
    if mask.size != size:
        mask = mask.resize(size, Image.NEAREST)
    return np.array(mask) > 127


def combine_masks(results: list[dict], size: tuple[int, int]) -> np.ndarray:
    """Fusionne les masques renvoyés par l'API en une seule carte (hauteur, largeur) d'identifiants.

    Chaque pixel vaut l'identifiant de sa classe (0 = fond par défaut). Un label inconnu lève une erreur
    au lieu d'être rangé en silence dans le fond, comme le faisait le notebook d'origine.
    """
    width, height = size
    combined = np.zeros((height, width), dtype=np.uint8)
    for result in results:
        label = result["label"]
        if label not in CLASS_TO_ID:
            raise ValueError(f"Label inattendu dans la réponse de l'API : {label!r}")
        if label == "Background":
            continue
        combined[decode_base64_mask(result["mask"], size)] = CLASS_TO_ID[label]
    return combined


def encode_mask_png(mask: np.ndarray) -> str:
    """Opération inverse de decode_base64_mask (sert aux tests et aux réponses simulées)."""
    buffer = io.BytesIO()
    Image.fromarray(mask.astype(np.uint8)).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def label_map_to_results(label_map: np.ndarray) -> list[dict]:
    """Construit une réponse au format de l'API à partir d'une carte de classes (pour simuler l'API)."""
    names = {i: name for name, i in CLASS_TO_ID.items()}
    return [
        {"label": names[int(c)], "score": 1.0, "mask": encode_mask_png((label_map == c) * 255)}
        for c in np.unique(label_map)
    ]
