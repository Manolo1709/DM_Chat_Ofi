# Guía rápida: La Taberna (App 2)

## 1. Variables

Copia `.env.example` a `.env` y rellena `LLM_API_KEY`, `VITE_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` y `FRONTEND_ORIGIN`. Nunca subas `.env` a Git.

La IA es Groq: `LLM_BASE_URL=https://api.groq.com/openai/v1` y `LLM_MODEL=qwen/qwen3.8-27b`. La clave (`gsk_...`) se crea en https://console.groq.com/keys.

## 2. Desarrollo local

```powershell
python -m venv .venv; .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn api.index:app --reload        # API en http://localhost:8000

npm install
npm run dev                           # SPA en http://localhost:5173
```

## 3. Pruebas

```powershell
pytest api/                           # backend, IA y Clerk simulados
npm test                              # frontend
npm run typecheck
```

## 4. Docker Compose (local)

```powershell
docker compose up -d --build          # http://localhost:8080
docker compose ps
docker compose logs -f backend
docker compose down
```

## 5. EC2

Sigue `aws/EC2.md`: `terraform apply` (crea también la IP elástica 52.21.114.192), apuntar el registro A de `lateberna.manoloplr.com` a esa IP, entrar por SSH, crear `.env` en la instancia con `DOMINIO=lateberna.manoloplr.com` y lanzar:

```bash
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build
```

Añade `https://lateberna.manoloplr.com` como origen permitido en Clerk. Para actualizar: `git pull` y el mismo comando. Al terminar, `terraform destroy`.

## 6. Comprobaciones de la demo

1. Entrada válida → resultado con `origen: "ia"`; repetir el cálculo da la misma tasa.
2. Peso 20 → mensaje de datos no válidos (422).
3. Sin sesión → botones de acceso; `curl -X POST https://lateberna.manoloplr.com/api/calcular` → 401.
4. https://lateberna.manoloplr.com abre por HTTPS con candado.
5. Once cálculos seguidos en un minuto → el último muestra «Has hecho demasiados cálculos».
