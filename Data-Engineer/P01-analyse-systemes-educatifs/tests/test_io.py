"""Tests du téléchargement sur un faux zip dans un dossier temporaire : data/raw/ n'est jamais touché."""

import hashlib
import zipfile

import pytest

from edstats import io

CSV_CONTENT = b"Country Code,Value\nFRA,1\nGBR,2\n"


@pytest.fixture
def fake_source(tmp_path, monkeypatch):
    """Un petit zip « publié » et un data/raw/ temporaire ; urlretrieve copie le zip au lieu du réseau."""
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("EdStatsCountry.csv", CSV_CONTENT)
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(io, "RAW_DIR", raw_dir)
    monkeypatch.setattr(io, "ZIP_PATH", raw_dir / "edstats.zip")
    monkeypatch.setattr(io, "ZIP_SHA256", hashlib.sha256(source.read_bytes()).hexdigest())

    def fake_urlretrieve(url, filename):
        filename.write_bytes(source.read_bytes())

    monkeypatch.setattr(io.urllib.request, "urlretrieve", fake_urlretrieve)
    return raw_dir


def test_sha256_of_small_file(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    assert io.sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_download_extracts_and_leaves_no_partial_file(fake_source):
    io.download()
    assert (fake_source / "EdStatsCountry.csv").read_bytes() == CSV_CONTENT
    assert not (fake_source / "edstats.zip.part").exists()


def test_download_with_wrong_hash_raises_and_keeps_no_zip(fake_source, monkeypatch):
    monkeypatch.setattr(io, "ZIP_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="force=True"):
        io.download()
    # le zip douteux n'a pas pris la place du vrai : le prochain appel retéléchargera
    assert not (fake_source / "edstats.zip").exists()


def test_download_rejects_existing_zip_with_wrong_hash(fake_source):
    fake_source.mkdir()
    (fake_source / "edstats.zip").write_bytes(b"pas un zip")
    with pytest.raises(ValueError, match="force=True"):
        io.download()


def test_truncated_csv_is_extracted_again(fake_source):
    io.download()
    csv = fake_source / "EdStatsCountry.csv"
    csv.write_bytes(CSV_CONTENT[:10])  # extraction interrompue
    io.download()
    assert csv.read_bytes() == CSV_CONTENT
