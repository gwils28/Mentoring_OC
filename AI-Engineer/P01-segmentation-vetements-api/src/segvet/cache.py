"""Mettre en cache les prédictions de l'API : les notebooks se rejouent ensuite sans token ni crédit."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from tqdm.auto import tqdm

from segvet.api import ApiError, SegformerClient
from segvet.io import PROJECT_DIR

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

# Variantes d'envoi : image allégée (choix du plan), PNG d'origine (comparaison prévue au plan) et JPEG
# pleine taille (ajoutée après coup : isole l'effet de la résolution, voir README)
VARIANTS = {
    "jpeg512": {"max_side": 512},
    "png": {"max_side": None, "as_png": True},
    "jpeg_pleine_taille": {"max_side": None},
}


def prediction_path(image_path: Path, variant: str, root: Path = PROCESSED_DIR) -> Path:
    return root / "predictions" / variant / f"pred_{image_path.stem.removeprefix('image_')}.png"


def log_path(variant: str, root: Path = PROCESSED_DIR) -> Path:
    return root / f"journal_appels_{variant}.jsonl"


def collect(
    client: SegformerClient,
    image_paths: list[Path],
    variants: tuple[str, ...] = ("jpeg512", "png"),
    root: Path = PROCESSED_DIR,
) -> dict[str, pd.DataFrame]:
    """Segmente chaque image absente du cache, pour chaque variante d'envoi, et journalise chaque appel.

    L'ordre des variantes alterne d'une image à l'autre (JPEG puis PNG, puis PNG puis JPEG…) : si l'API
    ralentit pendant la collecte, les deux variantes en pâtissent autant. Une image en échec est
    journalisée et n'arrête pas la boucle : mieux vaut 49 résultats et une erreur lisible qu'un notebook
    qui plante à la 40ᵉ image.
    """
    root.mkdir(parents=True, exist_ok=True)
    for i, image_path in enumerate(tqdm(image_paths, desc="images")):
        for variant in variants if i % 2 == 0 else variants[::-1]:
            target = prediction_path(image_path, variant, root)
            if target.exists():
                continue
            entry = {"image": image_path.name, "variant": variant, "order": i}
            try:
                label_map, info = client.segment(image_path, **VARIANTS[variant])
            except ApiError as error:
                entry |= {"status": "erreur", "message": str(error)}
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(label_map).save(target)
                entry |= {
                    "status": info.status,
                    "attempts": info.attempts,
                    "seconds": round(info.seconds, 3),
                    "total_seconds": round(info.total_seconds, 3),
                    "bytes_sent": info.bytes_sent,
                    "headers": info.headers,
                }
            with open(log_path(variant, root), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {variant: read_log(variant, root) for variant in variants}


def read_log(variant: str, root: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Journal des appels ; si une image a été retentée, on garde sa dernière ligne."""
    rows = [json.loads(line) for line in log_path(variant, root).read_text(encoding="utf-8").splitlines()]
    return pd.DataFrame(rows).drop_duplicates("image", keep="last").reset_index(drop=True)


def read_prediction(image_path: Path, variant: str, root: Path = PROCESSED_DIR) -> np.ndarray:
    return np.array(Image.open(prediction_path(image_path, variant, root)))
