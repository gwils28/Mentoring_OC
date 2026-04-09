"""Commande `agrireco` : une sous-commande par étape du pipeline, et `all` pour les enchaîner.

uv run agrireco prepare     # données brutes vérifiées → data/processed/dataset_consolide.csv
uv run agrireco train       # comparaison + optimisation + sélection (MLflow) → selection.json
uv run agrireco evaluate    # test final, recommandation, modèle servi → resultats.json, models/
uv run agrireco all         # les trois à la suite
"""

import argparse
import logging
import sys
import time

from agrireco.config import DEFAULT_CONFIG, load_config

log = logging.getLogger("agrireco")


def _step(name, func, cfg):
    log.info("▶ %s", name)
    start = time.perf_counter()
    func(cfg)
    log.info("✔ %s (%.0f s)", name, time.perf_counter() - start)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agrireco", description="Pipeline P12 : prepare → train → evaluate")
    parser.add_argument("step", choices=["prepare", "train", "evaluate", "all"])
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="fichier YAML de configuration")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Imports tardifs : `agrireco --help` reste instantané
    from agrireco.evaluate import run_evaluate, run_prepare
    from agrireco.train import run_train, setup_mlflow

    steps = {"prepare": run_prepare, "train": run_train, "evaluate": run_evaluate}
    try:
        cfg = load_config(args.config)
        # Un seul suivi MLflow pour toutes les étapes, quel que soit le dossier d'où l'on lance la commande
        setup_mlflow(cfg["paths"]["mlruns"])
        for name in steps if args.step == "all" else [args.step]:
            _step(name, steps[name], cfg)
    except (FileNotFoundError, ValueError) as err:
        # Erreur attendue (fichier absent, configuration invalide) : message clair et code de sortie non nul
        log.error("%s", err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
