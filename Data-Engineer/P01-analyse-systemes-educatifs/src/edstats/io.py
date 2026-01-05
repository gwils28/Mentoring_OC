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


def download(force: bool = False) -> Path:
    """Télécharge le zip si besoin, vérifie son empreinte puis l'extrait dans data/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force or not ZIP_PATH.exists():
        urllib.request.urlretrieve(DATA_URL, ZIP_PATH)
    found = sha256(ZIP_PATH)
    if found != ZIP_SHA256:
        raise ValueError(
            f"Empreinte inattendue pour {ZIP_PATH.name} : {found}. "
            "Le fichier source a changé : les résultats du corrigé ne sont plus garantis."
        )
    with zipfile.ZipFile(ZIP_PATH) as archive:
        missing = [n for n in archive.namelist() if not (RAW_DIR / n).exists()]
        archive.extractall(RAW_DIR, members=missing)
    return RAW_DIR


def load_tables() -> dict[str, pd.DataFrame]:
    """Retourne les 5 tables, indexées par leur nom court (« Country », « Data »…)."""
    download()
    return {name: pd.read_csv(RAW_DIR / f"EdStats{name}.csv") for name in TABLES}
