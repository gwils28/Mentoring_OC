"""Client de l'API serverless Hugging Face pour segformer_b3_clothes : token, timeout, quota, relances."""

import io
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv
from PIL import Image

from segvet.io import PROJECT_DIR
from segvet.masks import combine_masks

MODEL_ID = "sayeed99/segformer_b3_clothes"
# L'ancienne adresse api-inference.huggingface.co (celle du notebook d'origine) a été remplacée en 2025
# par le routeur des « Inference Providers » ; hf-inference est le service serverless de Hugging Face.
ENDPOINT = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

# Codes pour lesquels réessayer a un sens : quota dépassé, modèle en cours de chargement, panne passagère
RETRY_STATUSES = {429, 500, 502, 503, 504}
# Attente maximale acceptée quand le serveur demande de patienter (Retry-After) : au-delà, on préfère échouer
MAX_RETRY_AFTER = 60
# En-têtes de réponse gardés dans le journal : utiles au chiffrage, sans détail d'infrastructure
KEPT_HEADERS = {"x-inference-provider", "x-compute-time", "x-compute-type", "x-cache"}
# Codes pour lesquels réessayer ne sert à rien : il faut corriger quelque chose avant de relancer
FATAL_MESSAGES = {
    400: "requête refusée (image illisible ou mauvais Content-Type ?)",
    401: "token absent ou invalide : vérifiez HF_TOKEN dans le fichier .env",
    402: "crédits d'inférence épuisés sur ce compte Hugging Face",
    403: "ce token n'a pas le droit d'appeler les Inference Providers",
    404: "modèle ou adresse introuvable : vérifiez ENDPOINT",
}


class ApiError(RuntimeError):
    """Échec définitif d'un appel (après les éventuelles nouvelles tentatives)."""


def load_token(env_file: Path = PROJECT_DIR / ".env") -> str:
    """Lit HF_TOKEN depuis le fichier .env (jamais écrit dans le code, jamais affiché)."""
    load_dotenv(env_file)
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise ApiError(f"HF_TOKEN introuvable : créez {env_file} avec la ligne HF_TOKEN=hf_...")
    return token


WHOAMI_URL = "https://huggingface.co/api/whoami-v2"


def check_token(token: str, timeout: float = 10, session: requests.Session | None = None) -> str:
    """Requête simple qui valide le token : renvoie le nom du compte, sans jamais afficher le token."""
    response = (session or requests).get(
        WHOAMI_URL, headers={"Authorization": f"Bearer {token}"}, timeout=timeout
    )
    if response.status_code == 401:
        raise ApiError("token refusé par Hugging Face (401) : régénérez-le et mettez à jour .env")
    response.raise_for_status()
    return response.json()["name"]


def prepare_image(path: Path, max_side: int | None = 512, quality: int = 90) -> tuple[bytes, tuple[int, int]]:
    """Réduit l'image (plus grand côté ≤ max_side) et l'encode en JPEG pour alléger la requête.

    Le modèle redimensionne de toute façon chaque image en 512 × 512 : envoyer plus grand ne fait que
    ralentir le transfert. Renvoie les octets à envoyer et la taille (largeur, hauteur) envoyée.
    """
    image = Image.open(path).convert("RGB")
    if max_side is not None and max(image.size) > max_side:
        image.thumbnail((max_side, max_side), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue(), image.size


class RateLimiter:
    """Garantit au plus `max_per_minute` appels sur toute fenêtre glissante de 60 secondes."""

    def __init__(self, max_per_minute: int, clock=time.monotonic, sleep=time.sleep):
        if max_per_minute < 1:
            raise ValueError("max_per_minute doit valoir au moins 1")
        self.max_per_minute = max_per_minute
        self._clock, self._sleep = clock, sleep
        self._calls: deque[float] = deque()

    def wait(self) -> None:
        now = self._clock()
        while self._calls and now - self._calls[0] >= 60:
            self._calls.popleft()
        if len(self._calls) >= self.max_per_minute:
            self._sleep(60 - (now - self._calls[0]))
            self._calls.popleft()
        self._calls.append(self._clock())


@dataclass
class CallInfo:
    """Ce qu'on garde de chaque appel pour le rapport et le chiffrage."""

    status: int
    attempts: int
    seconds: float  # durée de la requête réussie (ce que le serveur a mis à répondre, réseau compris)
    bytes_sent: int
    headers: dict = field(default_factory=dict)
    total_seconds: float = 0.0  # en comptant les attentes du limiteur et les nouvelles tentatives


class SegformerClient:
    """Envoie une image au modèle et renvoie la carte de classes prédite."""

    def __init__(
        self,
        token: str,
        endpoint: str = ENDPOINT,
        timeout: float = 30,
        max_per_minute: int = 30,
        max_retries: int = 4,
        backoff: float = 2.0,
        session: requests.Session | None = None,
        clock=time.monotonic,
        sleep=time.sleep,
    ):
        self.endpoint, self.timeout = endpoint, timeout
        self.max_retries, self.backoff = max_retries, backoff
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"
        self.limiter = RateLimiter(max_per_minute, clock=clock, sleep=sleep)
        self._clock, self._sleep = clock, sleep

    def _delay(self, attempt: int, response: requests.Response | None) -> float:
        retry_after = response.headers.get("Retry-After") if response is not None else None
        if retry_after:
            # Deux formats possibles : un nombre de secondes, ou une date HTTP
            if retry_after.replace(".", "", 1).isdigit():
                return min(float(retry_after), MAX_RETRY_AFTER)
            try:
                wait = (parsedate_to_datetime(retry_after) - datetime.now(UTC)).total_seconds()
                return min(max(wait, 0.0), MAX_RETRY_AFTER)
            except (TypeError, ValueError):
                pass  # en-tête illisible : on garde l'attente par défaut
        return self.backoff * 2**attempt  # 2 s, 4 s, 8 s, 16 s

    def segment_bytes(self, data: bytes, content_type: str = "image/jpeg") -> tuple[list[dict], CallInfo]:
        """Un appel POST, avec nouvelles tentatives sur les erreurs passagères. Renvoie la réponse JSON."""
        start = self._clock()
        last_problem = ""
        for attempt in range(self.max_retries + 1):
            self.limiter.wait()
            response = None
            request_start = self._clock()
            try:
                response = self.session.post(
                    self.endpoint, data=data, headers={"Content-Type": content_type}, timeout=self.timeout
                )
            except (requests.Timeout, requests.ConnectionError) as error:
                last_problem = f"{type(error).__name__} (timeout = {self.timeout} s)"
            else:
                if response.status_code == 200:
                    info = CallInfo(
                        status=200,
                        attempts=attempt + 1,
                        seconds=self._clock() - request_start,
                        bytes_sent=len(data),
                        headers={
                            k.lower(): v for k, v in response.headers.items() if k.lower() in KEPT_HEADERS
                        },
                        total_seconds=self._clock() - start,
                    )
                    try:
                        results = response.json()
                    except ValueError as error:
                        raise ApiError("réponse inattendue : le corps n'est pas du JSON") from error
                    if not isinstance(results, list):
                        raise ApiError(
                            f"réponse inattendue : liste de masques attendue, reçu {str(results)[:120]}"
                        )
                    return results, info
                if response.status_code in FATAL_MESSAGES:
                    raise ApiError(f"HTTP {response.status_code} : {FATAL_MESSAGES[response.status_code]}")
                if response.status_code not in RETRY_STATUSES:
                    raise ApiError(f"HTTP {response.status_code} inattendu : {response.text[:200]}")
                last_problem = f"HTTP {response.status_code}"
            if attempt < self.max_retries:
                self._sleep(self._delay(attempt, response))
        raise ApiError(f"Échec après {self.max_retries + 1} tentatives : {last_problem}")

    def segment(
        self, path: Path, max_side: int | None = 512, as_png: bool = False
    ) -> tuple[np.ndarray, CallInfo]:
        """Segmente une image du disque ; la carte renvoyée a la taille de l'image d'origine.

        Par défaut l'image est allégée (JPEG, plus grand côté ≤ max_side). Avec as_png=True, le fichier PNG
        d'origine est envoyé tel quel (variante de comparaison du PLAN.md).
        """
        if as_png:
            if max_side is not None:
                raise ValueError("as_png envoie le fichier d'origine : passer max_side=None")
            results, info = self.segment_bytes(Path(path).read_bytes(), content_type="image/png")
        else:
            data, _ = prepare_image(path, max_side=max_side)
            results, info = self.segment_bytes(data)
        with Image.open(path) as image:
            size = image.size
        return combine_masks(results, size), info
