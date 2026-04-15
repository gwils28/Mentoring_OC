# Image de l'interface Streamlit (aucun modèle dedans : elle appelle l'API dont l'adresse est dans API_URL)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /srv
COPY app/requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt
COPY app/app.py app/app.py
RUN useradd --create-home appuser
USER appuser
EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
