import numpy as np
import pytest

from segvet.metrics import confusion_matrix, dice_per_class, iou_per_class, merge_classes, pixel_accuracy

TRUTH = np.array([[0, 0, 1, 1], [0, 0, 1, 1]])
PRED = np.array([[0, 0, 0, 1], [0, 0, 1, 2]])


def test_confusion_matrix_by_hand():
    cm = confusion_matrix(TRUTH, PRED, n_classes=3)
    np.testing.assert_array_equal(cm, [[4, 0, 0], [1, 2, 1], [0, 0, 0]])


def test_iou_and_dice_by_hand():
    cm = confusion_matrix(TRUTH, PRED, n_classes=3)
    # classe 1 : intersection 2, union 4 + 2 - 2 = 4 ; classe 2 : jamais vraie, prédite 1 fois → IoU 0
    np.testing.assert_allclose(iou_per_class(cm), [4 / 5, 2 / 4, 0.0])
    np.testing.assert_allclose(dice_per_class(cm), [8 / 9, 4 / 6, 0.0])


def test_dice_is_a_function_of_iou():
    rng = np.random.default_rng(0)
    cm = confusion_matrix(rng.integers(0, 4, (30, 30)), rng.integers(0, 4, (30, 30)), n_classes=4)
    iou = iou_per_class(cm)
    np.testing.assert_allclose(dice_per_class(cm), 2 * iou / (1 + iou))


def test_absent_class_is_nan_not_zero():
    cm = confusion_matrix(TRUTH, TRUTH, n_classes=4)
    assert np.isnan(iou_per_class(cm)[3])


def test_pixel_accuracy_is_flattered_by_background():
    truth = np.zeros((10, 10), int)
    truth[0, :5] = 1
    all_background = np.zeros_like(truth)
    cm = confusion_matrix(truth, all_background, n_classes=2)
    assert pixel_accuracy(cm) == 0.95
    assert iou_per_class(cm)[1] == 0.0


def test_shape_mismatch_is_an_error():
    with pytest.raises(ValueError):
        confusion_matrix(TRUTH, PRED[:, :3])


def test_merging_left_and_right_forgives_swaps():
    truth = np.array([[1, 2]])
    pred = np.array([[2, 1]])  # gauche et droite inversées
    cm = confusion_matrix(truth, pred, n_classes=3)
    assert np.nansum(iou_per_class(cm)[1:]) == 0
    merged = merge_classes(cm, [[0], [1, 2]])
    assert iou_per_class(merged)[1] == 1.0
    assert merged.sum() == cm.sum()


def test_merge_requires_a_partition():
    with pytest.raises(ValueError):
        merge_classes(np.eye(3, dtype=int), [[0], [1]])


@pytest.mark.parametrize("bad", [18, 255])
def test_confusion_matrix_rejects_unknown_class_ids(bad):
    # Sans contrôle, le couple (vérité 1, prédiction 18) tomberait en silence dans la case [2, 0]
    truth = np.array([[1, 0]])
    pred = np.array([[bad, 0]])
    with pytest.raises(ValueError, match="1 pixel"):
        confusion_matrix(truth, pred)
