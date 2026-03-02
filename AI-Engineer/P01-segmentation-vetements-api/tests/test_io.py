"""Tests du téléchargement sur un faux zip dans un dossier temporaire : data/raw/ n'est jamais touché."""

import hashlib
import io as stdio
import zipfile

import numpy as np
import pytest
from PIL import Image

from segvet import io


def _png(array: np.ndarray) -> bytes:
    buffer = stdio.BytesIO()
    Image.fromarray(array).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def fake_source(tmp_path, monkeypatch):
    """Un zip « publié » de 2 couples ; urlretrieve copie le zip au lieu d'aller sur le réseau."""
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        for n in (2, 10):
            archive.writestr(f"top_influenceurs_2024/IMG/image_{n}.png", _png(np.zeros((6, 4, 3), np.uint8)))
            archive.writestr(f"top_influenceurs_2024/Mask/mask_{n}.png", _png(np.full((6, 4), n, np.uint8)))
    raw = tmp_path / "raw"
    monkeypatch.setattr(io, "RAW_DIR", raw)
    monkeypatch.setattr(io, "ZIP_PATH", raw / "data.zip")
    monkeypatch.setattr(io, "DATASET_DIR", raw / "top_influenceurs_2024")
    monkeypatch.setattr(io, "ZIP_SHA256", hashlib.sha256(source.read_bytes()).hexdigest())
    monkeypatch.setattr(io.urllib.request, "urlretrieve", lambda url, f: f.write_bytes(source.read_bytes()))
    return raw


def test_sha256_of_small_file(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    assert io.sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_download_extracts_and_leaves_no_partial_file(fake_source):
    dataset = io.download()
    assert (dataset / "IMG" / "image_2.png").exists()
    assert not (fake_source / "data.zip.part").exists()


def test_download_refuses_wrong_hash(fake_source, monkeypatch):
    monkeypatch.setattr(io, "ZIP_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="Empreinte inattendue"):
        io.download()
    assert not (fake_source / "data.zip").exists()


def test_pairs_are_in_numeric_order(fake_source):
    dataset = io.download()
    pairs = io.list_pairs(dataset / "IMG", dataset / "Mask")
    assert [p[0].name for p in pairs] == ["image_2.png", "image_10.png"]
    assert io.read_mask(pairs[1][1]).max() == 10


def test_unpaired_image_is_an_error(fake_source):
    dataset = io.download()
    (dataset / "Mask" / "mask_10.png").unlink()
    with pytest.raises(ValueError, match=r"\[10\]"):
        io.list_pairs(dataset / "IMG", dataset / "Mask")
