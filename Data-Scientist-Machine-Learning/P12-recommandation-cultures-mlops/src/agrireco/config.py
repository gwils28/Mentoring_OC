"""Configuration centralisée : un seul fichier YAML (`config.yaml`) pilote tout le pipeline."""

from pathlib import Path
from typing import Any

import yaml

from agrireco.io import PROJECT_DIR

DEFAULT_CONFIG = PROJECT_DIR / "config.yaml"
REQUIRED_SECTIONS = ("paths", "seed", "split", "features", "models", "search", "recommendation")


def load_config(path: Path | str = DEFAULT_CONFIG) -> dict[str, Any]:
    """Lit la configuration et vérifie qu'elle est complète. Les chemins relatifs partent du projet."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {path}")
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    missing = [s for s in REQUIRED_SECTIONS if s not in cfg]
    if missing:
        raise ValueError(f"Configuration incomplète ({path}) : sections manquantes {missing}")
    cfg["paths"] = {k: (PROJECT_DIR / v).resolve() for k, v in cfg["paths"].items()}
    return cfg
