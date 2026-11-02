# Constitución de La Taberna (App 2)

Reglas del proyecto que ninguna especificación, plan, tarea o propuesta de la IA puede saltarse. Si una tarea entra en conflicto con este documento, gana la constitución.

## Principios fundamentales

### I. Aplicación mínima (NO NEGOCIABLE)

Una pantalla, un formulario, una llamada a la API de IA y un resultado. Están prohibidos: bases de datos y cualquier persistencia de entradas o resultados, CRUD, paneles o dashboards, pantallas, vistas o rutas de frontend adicionales, usuarios propios y funciones extra. El inicio de sesión de Clerk se integra como modal o componente dentro de la misma SPA, nunca como rutas propias.

### II. Seguridad primero: el cálculo lo hacen reglas, no la IA

La tasa de alcohol se calcula siempre en el servidor con la fórmula de Widmark (funciones puras y testeables). El nivel de embriaguez y los avisos de seguridad salen de reglas explícitas. La IA solo redacta la explicación y los consejos, y si falla se usa un texto genérico: el usuario nunca se queda sin resultado. Siempre se avisa de que no se debe conducir y de que el resultado es orientativo.

### III. Secretos solo en el backend (NO NEGOCIABLE)

La clave de la IA y la clave secreta de Clerk viven solo en variables de entorno del servidor. Nada sensible entra en Git, en las imágenes Docker, en el código del frontend, en las respuestas de la API, en los logs ni en las capturas. Solo las variables `VITE_*` públicas pueden llegar al navegador. El repositorio incluye `.env.example` con valores ficticios.

### IV. Contrato estable y entradas validadas

El frontend y el backend comparten un contrato JSON único (`src/types/alcohol.ts` ↔ `api/schemas.py`). Toda entrada se valida con límites (Pydantic) antes de llamar a la IA; una entrada inválida devuelve 422 sin llamar a la IA. A la IA solo se le envían números y valores de listas cerradas, nunca texto libre del usuario.

### V. Pruebas como evidencia

Cada requisito tiene al menos una prueba automática. Las pruebas usan un mock de la IA y nunca consumen créditos. Se prueban: entrada válida con una sola llamada, límites y vacíos, fallo externo y timeout, y acceso sin token o con token inválido (401 sin llamada a la IA).

### VI. Revisión humana de lo que propone la IA

Todo el código generado por la IA se revisa antes de integrarse. Las propuestas aceptadas y rechazadas se anotan para la comparativa entre App 1 y App 2.

## Restricciones técnicas

- Backend: Python 3.12 + FastAPI + Uvicorn. Pruebas con pytest.
- Frontend: Vue 3 + TypeScript + Vite + Tailwind CSS. Pruebas con Vitest.
- IA: un único proveedor compatible con la API de OpenAI (OpenRouter por defecto), con proveedor y modelo documentados.
- Autenticación: Clerk. El backend verifica el token de sesión antes de cualquier llamada a la IA.
- Despliegue: Docker Compose con dos contenedores (frontend compilado + FastAPI), red interna, puertos mínimos, secretos al ejecutar y sin servicios de datos. Una instancia AWS EC2 Linux con HTTPS, SSH restringido y retirada de recursos al terminar.
- Control de versiones: Git + GitHub, con la especificación commiteada antes del código que la implementa.

## Flujo de desarrollo

1. `/speckit-specify` → `spec.md` (qué y por qué, sin tecnología).
2. `/speckit-plan` → `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
3. `/speckit-tasks` → `tasks.md` con pasos pequeños y comprobables.
4. `/speckit-implement` → implementación con IA y revisión humana tarea a tarea.
5. Cada tarea cerrada deja un commit identificable de quien la hizo.

## Gobierno

Esta constitución prevalece sobre cualquier otra práctica del proyecto. Cambiarla exige acuerdo de todo el grupo, anotarlo en el historial de versiones y revisar que la spec, el plan y las tareas siguen cumpliéndola.

**Versión**: 1.0.0 | **Ratificada**: 2026-11-02 | **Última modificación**: 2026-11-02
