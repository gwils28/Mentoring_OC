"""Téléchargement vérifié des 50 images annotées fournies par ModeTrends (pièce jointe OpenClassrooms)."""

import hashlib
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "data" / "raw"
ZIP_PATH = RAW_DIR / "top_influenceurs_2024.zip"
DATA_URL = (
    "https://s3.eu-west-1.amazonaws.com/course.oc-static.com/projects/2053_AI+Engineer/"
    "top_influenceurs_2024-20250314T143221Z-001+(1).zip"
)
# Empreinte du zip publié par OpenClassrooms (vérifiée le 2026-10-24)
ZIP_SHA256 = "5195448b33774a7a7059f350c661b3401c35d8a159d2b8ef34504fd400f26a1a"

DATASET_DIR = RAW_DIR / "top_influenceurs_2024"
IMAGES_DIR = DATASET_DIR / "IMG"
MASKS_DIR = DATASET_DIR / "Mask"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _check_hash(path: Path) -> None:
    found = sha256(path)
    if found != ZIP_SHA256:
        raise ValueError(
            f"Empreinte inattendue pour {path} : {found} (attendue : {ZIP_SHA256}). "
            "Téléchargement corrompu ou fichier source modifié : les résultats du corrigé ne sont plus "
            f"garantis. Pour retélécharger : supprimer {ZIP_PATH} ou appeler download(force=True)."
        )


def download(force: bool = False) -> Path:
    """Télécharge le zip si besoin, vérifie son empreinte puis l'extrait dans data/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force or not ZIP_PATH.exists():
        # On télécharge à côté (.part) et on ne renomme qu'après vérification : un téléchargement
        # interrompu ne peut jamais se faire passer pour le vrai zip.
        partial = ZIP_PATH.with_name(ZIP_PATH.name + ".part")
        urllib.request.urlretrieve(DATA_URL, partial)
        try:
            _check_hash(partial)
        except ValueError:
            partial.unlink()
            raise
        partial.replace(ZIP_PATH)
    _check_hash(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        to_extract = [
            info
            for info in archive.infolist()
            if not (RAW_DIR / info.filename).exists()
            or (RAW_DIR / info.filename).stat().st_size != info.file_size
        ]
        archive.extractall(RAW_DIR, members=to_extract)
    return DATASET_DIR


def _number(path: Path) -> int:
    return int(re.search(r"(\d+)", path.stem).group(1))


def list_pairs(images_dir: Path = IMAGES_DIR, masks_dir: Path = MASKS_DIR) -> list[tuple[Path, Path]]:
    """Associe chaque image_N.png à son mask_N.png, dans l'ordre numérique (2 avant 10).

    Lève une erreur si une image n'a pas de masque (ou l'inverse) : on ne veut pas évaluer en silence
    sur un sous-ensemble.
    """
    images = {_number(p): p for p in images_dir.glob("image_*.png")}
    masks = {_number(p): p for p in masks_dir.glob("mask_*.png")}
    if images.keys() != masks.keys():
        orphans = sorted(images.keys() ^ masks.keys())
        raise ValueError(f"Images et masques non appariés pour les numéros {orphans}")
    return [(images[n], masks[n]) for n in sorted(images)]


def load_pairs() -> list[tuple[Path, Path]]:
    """Télécharge si besoin puis renvoie les 50 couples (image, masque annoté)."""
    download()
    return list_pairs()


def read_mask(path: Path) -> np.ndarray:
    """Masque annoté : tableau 2D d'entiers, un identifiant de classe (0 à 17) par pixel."""
    return np.array(Image.open(path))
