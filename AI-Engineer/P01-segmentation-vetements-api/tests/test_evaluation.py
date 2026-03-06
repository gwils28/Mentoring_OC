import numpy as np
import pytest

from segvet import evaluation as ev
from segvet.labels import CLASS_TO_ID, N_CLASSES


def _maps(seed, n=6, noise=0.0):
    """Cartes 20 × 20 aléatoires ; `noise` = part de pixels prédits au hasard."""
    rng = np.random.default_rng(seed)
    truths, preds = [], []
    for _ in range(n):
        truth = rng.integers(0, N_CLASSES, (20, 20))
        pred = truth.copy()
        flip = rng.random(truth.shape) < noise
        pred[flip] = rng.integers(0, N_CLASSES, flip.sum())
        truths.append(truth)
        preds.append(pred)
    return truths, preds


def test_perfect_prediction_scores_one():
    cms = ev.image_confusions(*_maps(0))
    assert ev.clothing_miou(cms.sum(axis=0)) == 1.0
    result = ev.bootstrap(cms, n_boot=50)
    assert result["ci"] == (1.0, 1.0) and result["degenerate_share"] == 0


def test_left_right_swap_is_forgiven_in_fused_view():
    truth = np.full((4, 4), CLASS_TO_ID["Left-shoe"])
    pred = np.full((4, 4), CLASS_TO_ID["Right-shoe"])
    table = ev.per_class_table(ev.image_confusions([truth], [pred]))
    assert table.loc["Chaussures", "iou"] == 1.0
    assert table.loc["Chaussures", "images"] == 1


def test_bootstrap_ci_contains_estimate_and_paired_delta_is_zero_for_same_data():
    cms = ev.image_confusions(*_maps(1, n=10, noise=0.3))
    result = ev.bootstrap(cms, n_boot=200, others=cms)
    low, high = result["ci"]
    assert low <= result["estimate"] <= high
    assert result["delta"] == 0 and result["delta_ci"] == (0, 0)


def test_better_variant_has_positive_paired_delta():
    truths, good = _maps(2, n=10, noise=0.1)
    _, bad = _maps(2, n=10, noise=0.5)
    result = ev.bootstrap(
        ev.image_confusions(truths, good), n_boot=200, others=ev.image_confusions(truths, bad)
    )
    assert result["delta_ci"][0] > 0


def test_decision_rule():
    table = ev.per_class_table(ev.image_confusions(*_maps(3)))
    assert ev.decision(0.61, table)[0] == "non disqualifié pour un pilote"
    assert ev.decision(0.59, table)[0] == "insuffisant"
    table.loc["Robe", "iou"] = 0.4
    assert ev.decision(0.9, table) == ("insuffisant", ["Robe"])


@pytest.mark.parametrize("missing", [np.nan])
def test_missing_key_garment_counts_as_weak(missing):
    table = ev.per_class_table(ev.image_confusions(*_maps(4)))
    table.loc["Jupe", "iou"] = missing
    assert "Jupe" in ev.decision(0.9, table)[1]
