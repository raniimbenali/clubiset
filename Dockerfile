# Image de base avec un tag explicite (jamais "latest")
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Utilisateur non root
RUN groupadd --system app \
    && useradd --system --gid app --no-create-home app \
    && chown app:app /app

# Les dependances d'abord : cette couche reste en cache tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app app ./app

USER app

EXPOSE 5000

# Docker interroge /health toutes les 10 secondes (python est deja dans l'image, pas besoin de curl)
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=3)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app:create_app()"]
