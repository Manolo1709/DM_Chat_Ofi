# Guía rápida: La Taberna (App 2)

## 1. Variables

Copia `.env.example` a `.env` y rellena `LLM_API_KEY`, `VITE_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` y `FRONTEND_ORIGIN`. Nunca subas `.env` a Git.

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
pytest                                # backend, IA y Clerk simulados
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

Sigue `aws/EC2.md`: `terraform apply`, entrar por SSH, crear `.env` en la instancia con `DOMINIO` y lanzar:

```bash
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build
```

Añade la URL `https://<ip-con-guiones>.sslip.io` como origen permitido en Clerk. Al terminar, `terraform destroy`.

## 6. Comprobaciones de la demo

1. Entrada válida → resultado con `origen: "ia"`.
2. Peso 20 → mensaje de datos no válidos (422).
3. Sin sesión → botones de acceso; `curl -X POST https://<dominio>/api/calcular` → 401.
4. La URL de EC2 abre por HTTPS con candado.
