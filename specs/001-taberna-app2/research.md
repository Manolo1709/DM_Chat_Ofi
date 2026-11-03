# Investigación y decisiones: La Taberna (App 2)

## D1. Quién calcula la tasa

- **Decisión**: el servidor, con la fórmula de Widmark (`api/calculo.py`). La IA solo explica.
- **Motivo**: en la App 1 la IA se equivocaba en las cuentas; un valor de seguridad debe ser reproducible y testeable.
- **Alternativas**: que la IA calcule y el servidor valide (descartada: resultados inestables y más llamadas fallidas).

## D2. Proveedor y modelo de IA

- **Decisión**: API compatible con OpenAI a través de Groq (`https://api.groq.com/openai/v1`), con el modelo configurable en `LLM_MODEL` (en producción `qwen/qwen3.8-27b`; en local `openai/gpt-oss-120b` con `LLM_REASONING_EFFORT=low`). Límites medidos: 1000 peticiones al día y 8000 tokens por minuto; respuesta de 0,5 a 1 s.
- **Motivo**: coste cero y posibilidad de cambiar de proveedor sin tocar el código.
- **Alternativas**: OpenRouter (se usó al principio; su modelo gratuito dejó de estar disponible y devolvía 404). Gemini directamente (se probó; con razonamiento activo cortaba el JSON si `LLM_REASONING_EFFORT` no era `none`).

## D3. Autenticación

- **Decisión**: Clerk con `@clerk/vue` en modal y `clerk-backend-api` (`authenticate_request`) en FastAPI, con `authorized_parties` = `FRONTEND_ORIGIN`.
- **Motivo**: lo exige el enunciado; evita usuarios propios y rutas extra.
- **Alternativas**: páginas `/sign-in` y `/sign-up` con vue-router (descartada: viola "una pantalla, sin rutas").

## D4. Límite de uso

- **Decisión**: 10 peticiones por minuto y 50 al día por usuario, en memoria con un `threading.Lock`.
- **Motivo**: proteger el crédito sin persistencia.
- **Limitación conocida**: no se comparte entre instancias ni sobrevive a un reinicio; aceptable con una sola instancia EC2.

## D5. Contenedores

- **Decisión**: dos contenedores (nginx con la SPA compilada y FastAPI + Uvicorn). El backend solo se expone en la red interna; nginx reenvía `/api`.
- **Motivo**: puertos mínimos y misma URL de origen para el frontend y la API (sin CORS).
- **Alternativas**: imagen única con supervisord (versión antigua en `docker/antiguo/`; descartada por mezclar responsabilidades).

## D6. Despliegue y HTTPS

- **Decisión**: EC2 `t3.micro` creada con Terraform, IP elástica, Caddy con Let's Encrypt y el dominio propio `lateberna.manoloplr.com` (registro A en Cloudflare, solo DNS).
- **Motivo**: HTTPS automático, una IP que no cambia y un origen estable para Clerk.
- **Alternativas**: ECS Fargate o App Runner (descartadas: el enunciado pide EC2 + Compose).
