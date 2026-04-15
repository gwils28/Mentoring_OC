# Image de l'API : Python 3.12 + dépendances figées (api/requirements.txt, généré depuis uv.lock)
# + package agrireco + modèle produit par le pipeline. Construire depuis le dossier du projet :
#   docker build -f api/Dockerfile -t agrireco-api .
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/gwils28/Mentoring_OC"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /srv

# Dépendances d'abord : cette couche reste en cache tant que requirements.txt ne change pas
COPY api/requirements.txt api/requirements.txt
RUN pip install -r api/requirements.txt

COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-deps .

COPY api/ api/
COPY models/model.joblib models/model.joblib

# Utilisateur sans privilèges
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --start-interval=2s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
