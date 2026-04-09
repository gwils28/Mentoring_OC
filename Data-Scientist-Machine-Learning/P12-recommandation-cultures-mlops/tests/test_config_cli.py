"""Configuration et commande `agrireco` : une erreur attendue donne un message clair, pas une trace."""

import pytest

from agrireco import cli
from agrireco.config import load_config


def test_default_config_is_complete():
    cfg = load_config()
    assert cfg["seed"] == 42
    assert cfg["paths"]["processed"].is_absolute()


def test_missing_config_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="introuvable"):
        load_config(tmp_path / "absent.yaml")


def test_incomplete_config(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("seed: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sections manquantes"):
        load_config(f)


def test_cli_returns_error_code_with_clear_message(tmp_path, caplog):
    f = tmp_path / "config.yaml"
    f.write_text("seed: 1\n", encoding="utf-8")
    assert cli.main(["train", "--config", str(f)]) == 1
    assert "sections manquantes" in caplog.text


def test_train_without_prepared_data_says_what_to_run(tmp_path, monkeypatch):
    from agrireco import train

    cfg = load_config()
    cfg["paths"]["processed"] = tmp_path  # aucun CSV consolidé ici
    with pytest.raises(FileNotFoundError, match="agrireco prepare"):
        train.load_train_test(cfg)


def test_cli_uses_project_mlflow_store_whatever_the_current_directory(tmp_path, monkeypatch):
    import mlflow

    from agrireco import evaluate

    seen = {}
    monkeypatch.chdir(tmp_path)  # lancé depuis un autre dossier
    monkeypatch.setattr(
        evaluate, "run_evaluate", lambda cfg: seen.setdefault("uri", mlflow.get_tracking_uri())
    )
    assert cli.main(["evaluate"]) == 0
    assert seen["uri"].endswith("mlruns/mlflow.db")
    assert not (tmp_path / "mlflow.db").exists()
