"""Téléchargement et chargement des 3 fichiers sources (DVF, population INSEE, référentiel géographique)."""

import hashlib
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
ZIP_PATH = RAW_DIR / "donnees_immo.zip"
# L'URL publiée contient un « é » décomposé (e + accent combinant, %CC%81) : la copier telle quelle.
DATA_URL = (
    "https://s3.eu-west-1.amazonaws.com/course.oc-static.com/projects/922_Data+Engineer/922_P3/"
    "Donne%CC%81es-immo+(2).zip"
)
# Empreinte du zip publié par OpenClassrooms (vérifiée le 2026-10-23)
ZIP_SHA256 = "50424e2c3a5831e9d1f647eb1910c48886794438ec638d05930883c6665b81cf"

# Nom court -> nom du fichier dans le zip
FILES = {
    "dvf": "Valeurs-foncières.xlsx",
    "population": "donnees_communes.xlsx",
    "referentiel": "fr-esr-referentiel-geographique.xlsx",
}


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
        # interrompu ou corrompu ne peut jamais se faire passer pour le vrai zip.
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
        # (extraction précédente interrompue = fichier tronqué).
        to_extract = [
            info
            for info in archive.infolist()
            if not (RAW_DIR / info.filename).exists()
            or (RAW_DIR / info.filename).stat().st_size != info.file_size
        ]
        archive.extractall(RAW_DIR, members=to_extract)
    return RAW_DIR


def load_sources() -> dict[str, pd.DataFrame]:
    """Retourne les 3 tables sources, tout en texte : les codes (« 01 », « 2A », « 001 ») gardent leurs zéros.

    Les conversions en nombres et en dates sont faites explicitement, colonne par colonne, dans prepare.py.
    """
    download()
    return {name: pd.read_excel(RAW_DIR / filename, dtype=str) for name, filename in FILES.items()}
