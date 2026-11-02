# 🐳 Docker Setup para **La Taberna** - Despliegue en AWS

Guía completa para contenerizar, testear localmente y desplegar en AWS (ECS Fargate / App Runner).

---

## 📦 Estructura de Archivos Docker

```
DM_Chat_v2/
├── Dockerfile                 # Multi-stage: build frontend + runtime Python (PRODUCCIÓN)
├── Dockerfile.dev             # Desarrollo con hot-reload (Vite + Uvicorn --reload)
├── docker-compose.yml         # Stack producción local (single container)
├── docker-compose.dev.yml     # Override para desarrollo con hot-reload
├── .dockerignore              # Excluye basura del contexto de build
├── docker/
│   └── supervisord.conf       # Para combined-dev (Vite + Uvicorn en un contenedor)
├── .github/workflows/
│   └── ci-cd.yml              # CI/CD GitHub Actions → ECR + ECS/App Runner
└── aws/
    ├── ecs-task-definition.json   # Plantilla Task Definition ECS Fargate
    └── apprunner-config.yaml      # Configuración App Runner
```

---

## 🚀 Inicio Rápido Local

### Opción A: Modo Producción (imagen final, sin hot-reload)
```bash
# 1. Copiar .env.example a .env y rellenar LLM_API_KEY
cp .env.example .env  # (crea este archivo con tus claves)

# 2. Levantar
docker compose up --build

# 3. Abrir http://localhost:8000
#    - Frontend servido por FastAPI en /
#    - API en /api/*
#    - Healthcheck en /api/health
```

### Opción B: Modo Desarrollo (hot-reload Vite + Uvicorn)
```bash
# Requiere Dockerfile.dev + docker-compose.dev.yml
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Puertos:
#   5173 → Vite dev server (frontend con HMR)
#   8000 → FastAPI + Uvicorn --reload (backend)
```

---

## ☁️ Despliegue en AWS

### Opción 1: **AWS App Runner** (Recomendado para simplicidad)
> Servicio totalmente gestionado, auto-scaling, HTTPS gratis, deploys desde ECR o GitHub.

**Pasos únicos (consola/CLI):**
```bash
# 1. Crear repo ECR
aws ecr create-repository --repository-name la-taberna --region eu-west-1

# 2. Crear secreto en Secrets Manager para la API key
aws secretsmanager create-secret \
  --name la-taberna/llm-api-key \
  --secret-string "sk-or-xxxxxxxxxxxx" \
  --region eu-west-1

# 3. Crear servicio App Runner (usando imagen de ECR)
aws apprunner create-service \
  --service-name la-taberna \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account>.dkr.ecr.eu-west-1.amazonaws.com/la-taberna:latest",
      "ImageConfiguration": { "Port": "8000" },
      "ImageRepositoryType": "ECR"
    },
    "AuthenticationConfiguration": { "AccessRoleArn": "arn:aws:iam::<account>:role/apprunner-ecr-role" }
  }' \
  --instance-configuration '{"Cpu": "0.25 vCPU", "Memory": "0.5 GB"}' \
  --region eu-west-1
```

**Deploy automático:** Push a `main` → GitHub Actions build + push a ECR → App Runner redeploy automático.

---

### Opción 2: **ECS Fargate** (Más control, ALB, VPC, WAF, etc.)

**Recursos necesarios:**
- VPC con subnets públicas/privadas
- ECS Cluster (Fargate)
- Application Load Balancer (ALB) + Target Group (puerto 8000, health check `/api/health`)
- Security Groups
- Task Execution Role + Task Role (permiso Secrets Manager)
- CloudWatch Log Group `/ecs/la-taberna`
- Secret en Secrets Manager: `la-taberna/llm-api-key`

**Task Definition:** Usa `aws/ecs-task-definition.json` como plantilla (reemplaza `${AWS_ACCOUNT_ID}`, `${AWS_REGION}`, `${IMAGE_URI}`).

**Deploy:** GitHub Actions actualiza task definition y hace `aws ecs deploy-task-definition`.

---

## 🔐 Variables de Entorno y Secretos

| Variable | Requerida | Descripción | Dónde |
|----------|-----------|-------------|-------|
| `LLM_API_KEY` | **Sí** (secreto) | Clave OpenRouter/OpenAI | Secrets Manager / GitHub Secrets |
| `LLM_BASE_URL` | No | Base URL API (default: `https://openrouter.ai/api/v1`) | Env / Task Def |
| `LLM_MODEL` | No | Modelo (default: `poolside/laguna-s-2.1:free`) | Env / Task Def |
| `LOG_ARCHIVO` | No | `false` en prod (solo stdout) | Env |
| `LOG_LEVEL` | No | `INFO` / `DEBUG` | Env |
| `APP_ENV` | No | `production` / `development` | Env |
| `UVICORN_WORKERS` | No | Workers Gunicorn (prod: 2-4) | Dockerfile / Env |

> **Importante:** Nunca pongas `LLM_API_KEY` en variables de entorno planas. Usa **Secrets Manager** (ECS/App Runner) o **GitHub Secrets** (CI).

---

## 🏗️ Detalles del Dockerfile (Producción)

### Multi-stage Build
```dockerfile
# Stage 1: frontend-builder (Node 22 Alpine)
#   - npm ci + npm run build → /app/frontend/dist

# Stage 2: runtime (Python 3.12 Slim)
#   - pip install -r requirements.txt
#   - COPY api/ → /app/api
#   - COPY --from=frontend-builder /app/frontend/dist → /app/static
#   - Usuario no-root (appuser:1001)
#   - Healthcheck integrado
#   - EXPOSE 8000
#   - CMD uvicorn api.index:app --host 0.0.0.0 --port 8000
```

### Optimizaciones
- **Cache layers**: `requirements.txt` y `package*.json` copiados antes que código
- **Multi-arch**: `docker buildx` builda `linux/amd64,linux/arm64` (Graviton)
- **Cache ECR**: `--cache-from/to type=registry` en CI
- **Non-root**: Usuario `appuser` UID 1001
- **Static files**: FastAPI sirve `/assets/*` (hash en nombre, cache largo) y SPA fallback `/*` → `index.html`

---

## 🧪 Testing en Contenedor

```bash
# Tests backend dentro del contenedor
docker compose run --rm app pytest api/ -v

# Tests frontend (requiere stage frontend-builder)
docker build --target frontend-builder -t la-taberna-frontend .
docker run --rm la-taberna-frontend npm test -- --run
```

---

## 📊 Healthcheck y Monitoreo

**Healthcheck endpoint:** `GET /api/health` → `{"status":"ok"}`

**Docker HEALTHCHECK:** Cada 30s, timeout 5s, 3 retries, start-period 15s.

**Logs:** Stdout/stderr → CloudWatch Logs (ECS/App Runner). Formato JSON estructurado por `api/registro.py`.

**Métricas sugeridas (CloudWatch):**
- `CPUUtilization`, `MemoryUtilization` (container insights)
- `RequestCount`, `TargetResponseTime`, `HTTPCode_Target_2XX/4XX/5XX` (ALB)
- Custom: `ia_fallback_total` (contar fallbacks IA → Widmark via logs)

---

## 💰 Estimación Costes AWS (eu-west-1, mes)

| Opción | Configuración | Coste aprox./mes |
|--------|---------------|------------------|
| **App Runner** | 0.25 vCPU, 0.5 GB, 1 instancia, 730h | **~$6-8 USD** |
| **ECS Fargate** | 0.25 vCPU, 0.5 GB, 1 task, ALB, 730h | **~$12-18 USD** |
| **ECR** | 1-2 GB storage, transfer | **~$0.20 USD** |
| **Secrets Manager** | 1 secreto, 10k API calls | **~$0.40 USD** |
| **CloudWatch Logs** | 1 GB ingest, 1 GB storage | **~$0.50 USD** |

> App Runner es ~40% más barato y cero gestión de infra. ECS da más control (VPC, WAF, sidecars, blue/green).

---

## 🛠️ Comandos Útiles

```bash
# Build local multi-arch (simula CI)
docker buildx create --use --name multiarch
docker buildx build --platform linux/amd64,linux/arm64 -t la-taberna:local .

# Inspeccionar imagen
docker run --rm la-taberna:local python -c "import api.calculo; print('OK')"

# Ver logs en tiempo real
docker compose logs -f app

# Ejecutar shell en contenedor corriendo
docker compose exec app bash

# Limpiar todo (imagenes, volumes, cache)
docker compose down -v --rmi all
docker system prune -a --volumes
```

---

## 🔧 Troubleshooting Común

| Problema | Solución |
|----------|----------|
| `404` en rutas frontend (recarga F5) | Verifica `spa_fallback` en `api/index.py` monta `/*` → `index.html` |
| `CORS` error en dev | Vite proxy en `vite.config.ts` → `target: http://127.0.0.1:8000` |
| `LLM_API_KEY` no encontrada | Revisa Secrets Manager ARN en task def / App Runner config |
| Healthcheck falla | Puerto 8000 expuesto? Security group permite ALB → task? |
| Frontend no carga assets | `docker compose build --no-cache` (cache de layer estático) |
| `ModuleNotFoundError: api.x` | `sys.path.insert(0, ...)` en `api/index.py` apunta a parent |

---

## 📚 Referencias

- [AWS App Runner Docs](https://docs.aws.amazon.com/apprunner/)
- [ECS Fargate Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [FastAPI Static Files + SPA](https://fastapi.tiangolo.com/tutorial/static-files/#single-page-application)

---

¿Dudas? Abre un issue o revisa los logs en CloudWatch. 🍺