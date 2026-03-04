import numpy as np
import pytest

from segvet.labels import CLASS_TO_ID, CLASSES, N_CLASSES
from segvet.masks import combine_masks, decode_base64_mask, encode_mask_png, label_map_to_results


def test_labels_match_model_config():
    assert N_CLASSES == 18
    assert CLASSES[4] == "Upper-clothes" and CLASS_TO_ID["Scarf"] == 17


def test_decode_resizes_with_nearest_neighbour():
    mask = np.zeros((2, 2), np.uint8)
    mask[0, 0] = 255
    decoded = decode_base64_mask(encode_mask_png(mask), size=(4, 4))
    assert decoded.dtype == bool
    assert decoded.sum() == 4  # le pixel devient un bloc 2 × 2, sans valeurs intermédiaires


def test_round_trip_api_format():
    label_map = np.array([[0, 4, 4], [6, 6, 11]], np.uint8)
    results = label_map_to_results(label_map)
    assert {r["label"] for r in results} == {"Background", "Upper-clothes", "Pants", "Face"}
    np.testing.assert_array_equal(combine_masks(results, size=(3, 2)), label_map)


def test_unknown_label_is_an_error():
    results = [{"label": "Sock", "score": 1.0, "mask": encode_mask_png(np.full((2, 2), 255))}]
    with pytest.raises(ValueError, match="Sock"):
        combine_masks(results, size=(2, 2))


def test_background_never_overwrites_a_garment():
    garment = np.full((2, 2), 255, np.uint8)
    results = [
        {"label": "Pants", "score": 1.0, "mask": encode_mask_png(garment)},
        {"label": "Background", "score": 1.0, "mask": encode_mask_png(garment)},
    ]
    assert (combine_masks(results, size=(2, 2)) == CLASS_TO_ID["Pants"]).all()
