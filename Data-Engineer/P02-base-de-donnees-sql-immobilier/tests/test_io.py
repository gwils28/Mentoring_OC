"""Tests du téléchargement sur un faux zip dans un dossier temporaire : data/raw/ n'est jamais touché."""

import hashlib
import io as stdio
import zipfile

import pandas as pd
import pytest

from dataimmo import io


def _xlsx_bytes(df: pd.DataFrame) -> bytes:
    buffer = stdio.BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


@pytest.fixture
def fake_source(tmp_path, monkeypatch):
    """Un petit zip « publié » (3 xlsx) et un data/raw/ temporaire ; urlretrieve copie au lieu du réseau."""
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        # « 01 » et « 001 » sont écrits en texte dans le xlsx, comme dans les vrais fichiers
        archive.writestr(
            io.FILES["dvf"], _xlsx_bytes(pd.DataFrame({"Code departement": ["01"], "Code postal": [1170]}))
        )
        archive.writestr(io.FILES["population"], _xlsx_bytes(pd.DataFrame({"CODCOM": ["001"]})))
        archive.writestr(io.FILES["referentiel"], _xlsx_bytes(pd.DataFrame({"reg_code": ["02"]})))
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(io, "RAW_DIR", raw_dir)
    monkeypatch.setattr(io, "ZIP_PATH", raw_dir / "donnees_immo.zip")
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
    assert all((fake_source / name).exists() for name in io.FILES.values())
    assert not (fake_source / "donnees_immo.zip.part").exists()


def test_download_with_wrong_hash_raises_and_keeps_no_zip(fake_source, monkeypatch):
    monkeypatch.setattr(io, "ZIP_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="force=True"):
        io.download()
    assert not (fake_source / "donnees_immo.zip").exists()


def test_download_rejects_existing_zip_with_wrong_hash(fake_source):
    fake_source.mkdir()
    (fake_source / "donnees_immo.zip").write_bytes(b"pas un zip")
    with pytest.raises(ValueError, match="force=True"):
        io.download()


def test_truncated_file_is_extracted_again(fake_source):
    io.download()
    xlsx = fake_source / io.FILES["dvf"]
    complet = xlsx.read_bytes()
    xlsx.write_bytes(complet[:10])  # extraction interrompue
    io.download()
    assert xlsx.read_bytes() == complet


def test_load_sources_reads_everything_as_text(fake_source):
    sources = io.load_sources()
    assert list(sources) == ["dvf", "population", "referentiel"]
    assert sources["dvf"].loc[0, "Code departement"] == "01"  # le zéro initial survit
    assert sources["dvf"].loc[0, "Code postal"] == "1170"  # nombre dans Excel, lu comme texte
    assert sources["population"].loc[0, "CODCOM"] == "001"
    assert sources["referentiel"].loc[0, "reg_code"] == "02"
