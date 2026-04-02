"""Tests du téléchargement sur un faux zip dans un dossier temporaire : data/raw/ n'est jamais touché."""

import hashlib
import io as stdio
import zipfile

import pytest

from agrireco import io


def _inner_zip(files: dict[str, str]) -> bytes:
    buffer = stdio.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


@pytest.fixture
def fake_source(tmp_path, monkeypatch):
    """Un zip « publié » qui contient deux zips, comme la pièce jointe OpenClassrooms."""
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(f"OC/{io.AGRI_ZIP}", _inner_zip({"crop_yield.csv": "Crop,Yield\nRice,1\n"}))
        archive.writestr(f"OC/{io.FAO_ZIP}", _inner_zip({"yield.csv": "Area\nPeru\n", "temp.csv": "year\n"}))
    raw = tmp_path / "raw"
    monkeypatch.setattr(io, "RAW_DIR", raw)
    monkeypatch.setattr(io, "ZIP_PATH", raw / "oc.zip")
    monkeypatch.setattr(io, "AGRI_DIR", raw / "agriculture_crop_yield")
    monkeypatch.setattr(io, "FAO_DIR", raw / "crop_yield_prediction")
    monkeypatch.setattr(io, "ZIP_SHA256", hashlib.sha256(source.read_bytes()).hexdigest())
    monkeypatch.setattr(io.urllib.request, "urlretrieve", lambda url, f: f.write_bytes(source.read_bytes()))
    return raw


def test_sha256_of_small_file(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    assert io.sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_download_extracts_both_datasets(fake_source):
    io.download()
    assert (fake_source / "agriculture_crop_yield" / "crop_yield.csv").read_text().startswith("Crop")
    assert (fake_source / "crop_yield_prediction" / "yield.csv").exists()
    assert (fake_source / "crop_yield_prediction" / "temp.csv").exists()


def test_bad_hash_leaves_nothing_behind(fake_source, monkeypatch):
    monkeypatch.setattr(io, "ZIP_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="Empreinte inattendue"):
        io.download()
    assert not (fake_source / "oc.zip").exists()
    assert not (fake_source / "oc.zip.part").exists()


def test_download_is_idempotent(fake_source):
    io.download()
    io.download()
    assert sorted(p.name for p in (fake_source / "crop_yield_prediction").iterdir()) == [
        "temp.csv",
        "yield.csv",
    ]


def test_missing_inner_zip_gives_clear_message(fake_source, monkeypatch):
    monkeypatch.setattr(io, "FAO_ZIP", "Autre jeu.zip")
    with pytest.raises(ValueError, match="absent du zip"):
        io.download()
