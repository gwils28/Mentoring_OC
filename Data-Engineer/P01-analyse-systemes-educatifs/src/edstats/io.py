"""Téléchargement et chargement des 5 fichiers EdStats (Banque mondiale)."""

import hashlib
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "data" / "raw"
ZIP_PATH = RAW_DIR / "edstats.zip"
DATA_URL = (
    "https://s3-eu-west-1.amazonaws.com/static.oc-static.com/prod/courses/files/"
    "Parcours_data_scientist/Projet+-+Donn%C3%A9es+%C3%A9ducatives/"
    "Projet+Python_Dataset_Edstats_csv.zip"
)
# Empreinte du zip publié par OpenClassrooms (vérifiée le 2026-01-05)
ZIP_SHA256 = "8ccdd02f411e3f067499253ed577d107e9612f94d6141961ad7dc591f92fd32c"

TABLES = ["Country", "Series", "Country-Series", "FootNote", "Data"]


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
        # interrompu ou corrompu ne peut jamais se faire passer pour le vrai edstats.zip.
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
        # On (ré)extrait tout fichier absent ou dont la taille diffère de celle annoncée dans le zip
        # (extraction précédente interrompue = CSV tronqué).
        to_extract = [
            info
            for info in archive.infolist()
            if not (RAW_DIR / info.filename).exists()
            or (RAW_DIR / info.filename).stat().st_size != info.file_size
        ]
        archive.extractall(RAW_DIR, members=to_extract)
    return RAW_DIR


def load_tables() -> dict[str, pd.DataFrame]:
    """Retourne les 5 tables, indexées par leur nom court (« Country », « Data »…)."""
    download()
    return {name: pd.read_csv(RAW_DIR / f"EdStats{name}.csv") for name in TABLES}
