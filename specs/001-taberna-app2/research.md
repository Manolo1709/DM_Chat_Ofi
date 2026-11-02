# Investigación y decisiones: La Taberna (App 2)

## D1. Quién calcula la tasa

- **Decisión**: el servidor, con la fórmula de Widmark (`api/calculo.py`). La IA solo explica.
- **Motivo**: en la App 1 la IA se equivocaba en las cuentas; un valor de seguridad debe ser reproducible y testeable.
- **Alternativas**: que la IA calcule y el servidor valide (descartada: resultados inestables y más llamadas fallidas).

## D2. Proveedor y modelo de IA

- **Decisión**: API compatible con OpenAI a través de OpenRouter, modelo gratuito `poolside/laguna-s-2.1:free`, configurable con `LLM_BASE_URL` y `LLM_MODEL`.
- **Motivo**: coste cero y posibilidad de cambiar de proveedor sin tocar el código.
- **Alternativas**: Gemini directamente (se probó; con razonamiento activo cortaba el JSON si `LLM_REASONING_EFFORT` no era `none`).

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

- **Decisión**: EC2 `t3.micro` creada con Terraform, Caddy con Let's Encrypt y dominio `sslip.io` derivado de la IP.
- **Motivo**: HTTPS automático sin comprar dominio; Clerk exige un origen HTTPS.
- **Alternativas**: ECS Fargate o App Runner (descartadas: el enunciado pide EC2 + Compose).
