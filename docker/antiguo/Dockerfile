# =====================================================================
# La Taberna - Multi-stage Dockerfile para AWS (ECS Fargate, App Runner, ECR)
# =====================================================================
# Etapa 1: Build del frontend (Vite + Vue 3)
# Etapa 2: Runtime Python (FastAPI) sirviendo API + estáticos del frontend
# =====================================================================

# ---------------------------------------------------------------------
# STAGE 1: Frontend Builder
# ---------------------------------------------------------------------
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Cache de dependencias
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit --no-fund

# Build de la app
COPY src/ ./src/
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig*.json ./
COPY public/ ./public/ 2>/dev/null || true

# Variable para desactivar mock en build de producción
ARG VITE_USE_MOCK=false
ENV VITE_USE_MOCK=${VITE_USE_MOCK}

RUN npm run build

# ---------------------------------------------------------------------
# STAGE 2: Python Runtime (FastAPI + Static Files)
# ---------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Metadatos
LABEL maintainer="Manolo1709"
LABEL description="Calculadora de alcohol en sangre - La Taberna"
LABEL version="1.0.0"

# Variables de entorno por defecto (sobrescribibles en AWS)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # FastAPI
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000 \
    UVICORN_WORKERS=1 \
    # Logs
    LOG_ARCHIVO=false \
    LOG_LEVEL=INFO \
    # App
    APP_ENV=production

# Usuario no-root para seguridad
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --home /app --shell /sbin/nologin appuser

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python (cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la API
COPY api/ ./api/

# Copiar frontend construido desde stage anterior
COPY --from=frontend-builder /app/frontend/dist ./static

# Crear directorio de logs y dar permisos
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

# Cambiar a usuario no-root
USER appuser

# Healthcheck para AWS (ALB/ECS)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=3)" || exit 1

# Puerto expuesto
EXPOSE 8000

# Comando de arranque
# Usamos uvicorn directo; para producción con workers: gunicorn -k uvicorn.workers.UvicornWorker api.index:app
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]