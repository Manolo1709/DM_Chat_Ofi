# Contenedor del backend: FastAPI + Uvicorn.
# Solo expone la API dentro de la red de Docker Compose; el navegador
# llega a ella a través del contenedor del frontend (nginx).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Sin archivo de errores: los avisos salen por consola (docker compose logs)
    LOG_ARCHIVO=false

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt uvicorn==0.54.0

COPY api/ ./api/

# Usuario sin privilegios
RUN useradd --system --uid 1001 --home /app appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=3)" || exit 1

CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
