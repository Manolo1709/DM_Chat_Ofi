# Docker: La Taberna (App 2)

La aplicación corre en dos contenedores unidos con Docker Compose.

```
Navegador ──HTTP──> frontend (nginx, puerto 8080) ──/api/*──> backend (FastAPI, 8000) ──> API de IA
                    sirve la SPA compilada          red interna   valida, Clerk, IA o fórmula
```

| Contenedor | Imagen base | Qué hace | Puerto |
|---|---|---|---|
| `taberna-frontend` | `node:22-alpine` para compilar, `nginx:1.27-alpine` para servir | Sirve la SPA de Vue y reenvía `/api/*` al backend | 8080 en el equipo (80 dentro) |
| `taberna-backend` | `python:3.12-slim` | FastAPI con Uvicorn; guarda la clave de la IA y verifica Clerk | 8000, solo en la red interna |

- El navegador solo habla con nginx: un único origen, así que no hace falta CORS.
- El backend no publica ningún puerto: desde fuera no se puede llamar a la API saltándose nginx.
- No hay base de datos, caché ni volúmenes de datos. Los avisos del backend salen por consola (`docker compose logs`).
- Los secretos (`LLM_API_KEY`, `CLERK_SECRET_KEY`) se leen de `.env` al arrancar; no se copian a las imágenes ni se suben a Git.

## Archivos

| Archivo | Para qué |
|---|---|
| `docker-compose.yml` | Define los dos servicios, el puerto y las variables |
| `docker/backend.Dockerfile` | Imagen del backend |
| `docker/frontend.Dockerfile` | Compila el frontend y lo copia a nginx |
| `docker/nginx.conf` | Sirve la SPA y hace de proxy de `/api/` |
| `.dockerignore` | Deja fuera `.env`, `node_modules`, tests y documentación |

## Variables en `.env`

| Variable | Contenedor | Nota |
|---|---|---|
| `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | backend | Proveedor de IA |
| `CLERK_SECRET_KEY` | backend | Secreta |
| `FRONTEND_ORIGIN` | backend | Por defecto `http://localhost:8080`; en EC2, la URL pública con https |
| `VITE_CLERK_PUBLISHABLE_KEY` | frontend (al compilar) | Pública; si cambia hay que reconstruir |
| `PUERTO_WEB` | frontend | Opcional, por defecto 8080 |

## Uso

```bash
docker compose up -d --build     # construir y arrancar
docker compose ps                # los dos deben salir "running" (el backend, "healthy")
docker compose logs -f backend   # ver los avisos de la API
docker compose down              # parar
```

Abrir http://localhost:8080. Comprobación rápida: http://localhost:8080/api/health devuelve `{"status":"ok"}`.

La configuración anterior de un solo contenedor (y la de App Runner/ECS) está en `docker/antiguo/` por si hace falta consultarla.
