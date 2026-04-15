"""Tests de l'API avec le modèle versionné (models/model.joblib) : aucun réseau, aucune donnée brute."""

import pytest
from fastapi.testclient import TestClient

from api.main import app

CTX = {"avg_temp": 20.0, "rainfall_mm": 1000.0, "pesticides_t": 5000.0}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # le `with` déclenche le chargement du modèle au démarrage
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["crops"] == 10


def test_predict_returns_positive_yield(client):
    r = client.post("/predict", json={**CTX, "crop": "Maize"})
    assert r.status_code == 200
    body = r.json()
    assert body["yield_t_ha"] > 0
    assert body["out_of_range"] == []


def test_predict_unknown_crop_is_422(client):
    r = client.post("/predict", json={**CTX, "crop": "Banana"})
    assert r.status_code == 422
    assert "Culture inconnue" in r.json()["detail"]


@pytest.mark.parametrize(
    "field, value", [("avg_temp", 80), ("rainfall_mm", -1), ("pesticides_t", "beaucoup")]
)
def test_invalid_context_is_422(client, field, value):
    r = client.post("/predict", json={**CTX, "crop": "Maize", field: value})
    assert r.status_code == 422


def test_missing_field_is_422(client):
    r = client.post("/recommend", json={"avg_temp": 20.0})
    assert r.status_code == 422


def test_recommend_ranks_all_crops_by_relative_yield(client):
    r = client.post("/recommend", json=CTX)
    assert r.status_code == 200
    ranking = r.json()["ranking"]
    assert len(ranking) == 10
    # Cultures appuyées par des données proches d'abord, chaque bloc trié par rendement relatif
    supported = [c["crop_supported"] for c in ranking]
    assert supported == sorted(supported, reverse=True)
    for flag in (True, False):
        rel = [c["relative_yield"] for c in ranking if c["crop_supported"] is flag]
        assert rel == sorted(rel, reverse=True)
    assert [c["rank"] for c in ranking] == list(range(1, 11))
    assert "rentabilité" in r.json()["note"]


def test_extrapolation_is_flagged(client):
    r = client.post("/recommend", json={**CTX, "avg_temp": 40.0})
    assert "avg_temp" in r.json()["out_of_range"]


def test_predict_matches_recommend(client):
    """La même culture dans les mêmes conditions donne le même rendement par les deux routes."""
    pred = client.post("/predict", json={**CTX, "crop": "Wheat"}).json()["yield_t_ha"]
    reco = {c["crop"]: c["yield_t_ha"] for c in client.post("/recommend", json=CTX).json()["ranking"]}
    assert reco["Wheat"] == pytest.approx(pred)


def test_unsupported_crop_never_ranked_first_in_cold_climate(client):
    cold = {"avg_temp": 8.0, "rainfall_mm": 600.0, "pesticides_t": 20000.0}
    first = client.post("/recommend", json=cold).json()["ranking"][0]
    assert first["crop_supported"]


def test_served_bundle_does_not_depend_on_pyarrow():
    """L'image Docker n'installe pas pyarrow : le modèle picklé ne doit pas y faire référence."""
    import pickle

    import joblib  # noqa: E401

    from api.main import MODEL_PATH

    raw = pickle.dumps(joblib.load(MODEL_PATH))
    assert b"pyarrow" not in raw


def test_bundle_reloads_in_a_process_without_pyarrow():
    """Comme dans l'image Docker : pyarrow bloqué, le modèle doit quand même se recharger."""
    import subprocess
    import sys

    from api.main import MODEL_PATH

    code = f"import sys; sys.modules['pyarrow'] = None; import joblib; joblib.load(r'{MODEL_PATH}')"
    subprocess.run([sys.executable, "-c", code], check=True)


def test_load_bundle_refuses_missing_file_and_other_sklearn_version(tmp_path):
    import joblib

    from agrireco import service
    from api.main import MODEL_PATH

    with pytest.raises(FileNotFoundError, match="agrireco evaluate"):
        service.load_bundle(tmp_path / "absent.joblib")
    bundle = joblib.load(MODEL_PATH)
    bundle.metadata["sklearn_version"] = "0.0.1"
    joblib.dump(bundle, tmp_path / "vieux.joblib")
    with pytest.raises(RuntimeError, match="scikit-learn 0.0.1"):
        service.load_bundle(tmp_path / "vieux.joblib")
