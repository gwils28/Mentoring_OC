"""Mesure : temps d'inférence locale sur N cœurs + accord avec les prédictions de l'API (variante png).

Usage : uv run --group local python scripts/mesure_inference_locale.py 2
"""

import json
import sys
import time

import numpy as np
import torch

from segvet import cache, io, local
from segvet import evaluation as ev

threads = int(sys.argv[1])
torch.set_num_threads(threads)
processor, model = local.load_model()
pairs = io.load_pairs()
local.predict(pairs[0][0], processor, model)  # échauffement
times, agree, preds = [], [], []
for img, _ in pairs:
    t0 = time.perf_counter()
    p = local.predict(img, processor, model)
    times.append(time.perf_counter() - t0)
    preds.append(p)
    agree.append(float((p == cache.read_prediction(img, "png")).mean()))
truths = [io.read_mask(m) for _, m in pairs]
miou = ev.clothing_miou(ev.image_confusions(truths, preds).sum(axis=0))
out = {
    "threads": threads,
    "cpu": open("/proc/cpuinfo").read().split("model name")[1].split("\n")[0].strip(": \t"),
    "median_s": float(np.median(times)),
    "p95_s": float(np.percentile(times, 95)),
    "accord_pixels_api_png_median": float(np.median(agree)),
    "accord_min": float(min(agree)),
    "miou_vetements_local": miou,
    "torch": torch.__version__,
}
print(json.dumps(out, ensure_ascii=False))
