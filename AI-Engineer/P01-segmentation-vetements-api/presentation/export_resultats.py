"""Exporte les chiffres du corrigé pour la présentation : aucun chiffre saisi à la main dans les diapositives.

Usage : uv run python presentation/export_resultats.py  (puis : cd presentation && npm run build)
"""

import json
from pathlib import Path

import numpy as np

from segvet import cache, cost, io
from segvet import evaluation as ev
from segvet.metrics import confusion_matrix, pixel_accuracy

SORTIE = Path(__file__).with_name("resultats.json")
N_IMAGES, JOURS = 500_000, 30
# Facture lue sur la page « Inference Providers » du compte (2026-10-24) : 301 requêtes, « < 0,01 $ »
FACTURE_MAX, REQUETES_FACTUREES = 0.01, 301
# Grille Hugging Face (Inference Endpoints, AWS), lue le 2026-10-24
CPU_HEURE, T4_HEURE = 0.07, 0.50


def main() -> None:
    pairs = io.load_pairs()
    verites = [io.read_mask(m) for _, m in pairs]
    preds = {v: [cache.read_prediction(i, v) for i, _ in pairs] for v in cache.VARIANTS}
    cms = {v: ev.image_confusions(verites, p) for v, p in preds.items()}
    boot = ev.bootstrap(cms["jpeg512"], n_boot=2000, seed=0, others=cms["png"])
    table = ev.per_class_table(cms["jpeg512"])
    verdict, faibles = ev.decision(boot["ci"][0], table)
    total = cms["jpeg512"].sum(axis=0)
    tout_fond = sum(confusion_matrix(v, np.zeros_like(v)) for v in verites)
    journaux = {v: cache.read_log(v) for v in cache.VARIANTS}
    lat = journaux["jpeg512"].query("attempts == 1")["seconds"]
    bench = json.loads((cache.PROCESSED_DIR / "mesure_inference_locale.json").read_text())
    t_cloud = 2 * next(m["median_s"] for m in bench["mesures"] if m["threads"] == 2)
    heures_lots = cost.batch_hours(N_IMAGES, t_cloud)
    resultats = {
        "miou": round(boot["estimate"], 3),
        "ic": [round(x, 3) for x in boot["ci"]],
        "verdict": verdict,
        "vetements_faibles": faibles,
        "iou": {g: round(float(v), 3) for g, v in table["iou"].items()},
        "images_par_famille": {g: int(v) for g, v in table["images"].items()},
        "exactitude_modele": round(pixel_accuracy(total), 3),
        "exactitude_tout_fond": round(pixel_accuracy(tout_fond), 3),
        "delta_jpeg_png": round(boot["delta"], 4),
        "ko_jpeg": round(journaux["jpeg512"]["bytes_sent"].median() / 1000),
        "ko_png": round(journaux["png"]["bytes_sent"].median() / 1000),
        "latence_mediane": round(float(lat.median()), 2),
        "latence_p95": round(float(lat.quantile(0.95)), 2),
        "appels_reussis": int(sum((j["status"] == 200).sum() for j in journaux.values())),
        "debit_requis_min": round(cost.required_rate_per_minute(N_IMAGES, JOURS), 1),
        "cout": {
            "serverless_max": round(cost.serverless_cost(N_IMAGES, 1, FACTURE_MAX / REQUETES_FACTUREES), 1),
            "cpu_continu": round(cost.dedicated_cost(24 * JOURS, CPU_HEURE), 1),
            "t4_continu": round(cost.dedicated_cost(24 * JOURS, T4_HEURE), 1),
            "cpu_lots": round(cost.dedicated_cost(heures_lots, CPU_HEURE), 1),
            "heures_lots": round(heures_lots),
            "debit_cpu_min": round(60 / t_cloud),
        },
    }
    SORTIE.write_text(json.dumps(resultats, ensure_ascii=False, indent=1))
    print(json.dumps(resultats, ensure_ascii=False))


if __name__ == "__main__":
    main()
