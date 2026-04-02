"""Téléchargement vérifié des deux jeux de données fournis par OpenClassrooms (pièce jointe de la mission).

Le zip publié contient lui-même deux zips : « Agriculture Crop Yield » (jeu synthétique, 1 fichier) et
« Crop Yield Prediction Dataset » (FAO et Banque mondiale, 5 fichiers). Les deux sont extraits dans data/raw/.
"""

import hashlib
import io as stdio
import urllib.request
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "data" / "raw"
ZIP_PATH = RAW_DIR / "oc_p12_dsml.zip"
DATA_URL = (
    "https://s3.eu-west-1.amazonaws.com/course.oc-static.com/projects/1047_Data+Scientist+ML/"
    "P12_DSML_1047/OC-20250526T142605Z-1-001.zip"
)
# Empreinte du zip publié par OpenClassrooms (vérifiée le 2026-10-25)
ZIP_SHA256 = "a387e4f347ee0cf33f20b323a26c0c02fd44d8b54849bf94f1bdbb84b51f039a"

AGRI_ZIP = "Agriculture Crop Yield.zip"
FAO_ZIP = "Crop Yield Prediction Dataset.zip"
AGRI_DIR = RAW_DIR / "agriculture_crop_yield"
FAO_DIR = RAW_DIR / "crop_yield_prediction"


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


def _extract_inner(outer: zipfile.ZipFile, inner_name: str, target: Path) -> None:
    """Extrait le zip interne `inner_name` (où qu'il soit dans l'archive) vers `target`, à plat."""
    member = next((n for n in outer.namelist() if n.endswith(inner_name)), None)
    if member is None:
        raise ValueError(f"« {inner_name} » absent du zip téléchargé : la pièce jointe a changé de contenu.")
    with zipfile.ZipFile(stdio.BytesIO(outer.read(member))) as inner:
        target.mkdir(parents=True, exist_ok=True)
        for info in inner.infolist():
            if info.is_dir():
                continue
            out = target / Path(info.filename).name
            if not out.exists() or out.stat().st_size != info.file_size:
                out.write_bytes(inner.read(info))


def download(force: bool = False) -> tuple[Path, Path]:
    """Télécharge le zip si besoin, vérifie son empreinte, extrait les deux jeux.

    Renvoie (dossier du jeu synthétique, dossier du jeu FAO).
    """
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
    with zipfile.ZipFile(ZIP_PATH) as outer:
        _extract_inner(outer, AGRI_ZIP, AGRI_DIR)
        _extract_inner(outer, FAO_ZIP, FAO_DIR)
    return AGRI_DIR, FAO_DIR
