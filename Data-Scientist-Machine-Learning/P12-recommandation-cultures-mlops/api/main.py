"""API de prédiction et de recommandation (FastAPI).

Volontairement mince : elle valide les entrées, charge le modèle produit par le pipeline et délègue tout
le calcul à `agrireco.service`. Lancer en local depuis le dossier du projet :

    uv run uvicorn api.main:app --reload        # puis http://localhost:8000/docs
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agrireco import service

MODEL_PATH = Path(
    os.environ.get("MODEL_PATH", Path(__file__).resolve().parents[1] / "models" / "model.joblib")
)
log = logging.getLogger("agrireco.api")
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargé une fois au démarrage : si le fichier manque, l'API refuse de démarrer (message explicite)
    state["bundle"] = service.load_bundle(MODEL_PATH)
    log.info("Modèle chargé : %s", state["bundle"].metadata.get("modele"))
    yield
    state.clear()


app = FastAPI(
    title="Agritech Answers — rendement et recommandation de cultures",
    description=(
        "Prédit le rendement **moyen national** d'une culture pour un pays aux conditions données "
        "(niveau technique moyen 1990-2013). Ce n'est pas une prédiction à la parcelle."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class Context(BaseModel):
    """Conditions d'un pays-type (moyennes nationales annuelles). Bornes physiques larges ; le domaine
    observé à l'entraînement est signalé dans la réponse."""

    avg_temp: float = Field(..., ge=-15, le=45, description="Température moyenne annuelle (°C)")
    rainfall_mm: float = Field(..., ge=0, le=5000, description="Pluie annuelle normale (mm)")
    pesticides_t: float = Field(
        ..., ge=0, le=5_000_000, description="Pesticides utilisés dans le pays (tonnes)"
    )


class PredictRequest(Context):
    crop: str = Field(..., description="Culture (voir GET /crops)")


class PredictResponse(BaseModel):
    crop: str
    yield_t_ha: float
    relative_yield: float
    out_of_range: list[str]
    crop_supported: bool


class RankedCrop(BaseModel):
    rank: int
    crop: str
    yield_t_ha: float
    relative_yield: float
    crop_supported: bool


class RecommendResponse(BaseModel):
    ranking: list[RankedCrop]
    out_of_range: list[str]
    note: str


@app.get("/health")
def health() -> dict:
    bundle = state["bundle"]
    return {"status": "ok", "model": bundle.metadata.get("modele"), "crops": len(bundle.crops)}


@app.get("/crops")
def crops() -> list[str]:
    return state["bundle"].crops


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> dict:
    try:
        return service.predict(state["bundle"], req.crop, req.avg_temp, req.rainfall_mm, req.pesticides_t)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


@app.post("/recommend", response_model=RecommendResponse)
def recommend(ctx: Context) -> dict:
    bundle = state["bundle"]
    out = service.recommend_crops(bundle, ctx.avg_temp, ctx.rainfall_mm, ctx.pesticides_t)
    note = (
        "Classement par rendement relatif (rendement prédit ÷ rendement habituel de la culture). "
        "Ce n'est pas un classement par rentabilité : aucun prix n'est pris en compte."
    )
    if bundle.metadata.get("modele") in ("ridge", "baseline"):
        note += (
            " Avec ce modèle (additif), l'ordre des cultures ne dépend pas des conditions ; seules changent "
            "les cultures reléguées en fin de liste faute de pays aux conditions proches qui les cultivent."
        )
    return {**out, "note": note}
