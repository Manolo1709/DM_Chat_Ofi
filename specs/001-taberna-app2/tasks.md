---
description: "Lista de tareas de La Taberna (App 2)"
---

# Tareas: La Taberna (App 2)

**Entrada**: documentos de diseño de `/specs/001-taberna-app2/`

**Requisitos previos**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Pruebas**: obligatorias según la constitución (principio V).

**Estado**: `[X]` hecha y revisada, `[ ]` pendiente. Las tareas marcadas se reutilizan de la App 1 o ya están implementadas; las pendientes son las que faltan para entregar.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: se puede hacer en paralelo (otros archivos, sin dependencias)
- **[US#]**: historia de usuario de `spec.md`

---

## Fase 1: Preparación

- [X] T001 Estructura `api/` + `src/` + `tests/` reutilizada de la App 1
- [X] T002 [P] Dependencias de Python en `requirements.txt` y `requirements-dev.txt` (añadir `clerk-backend-api`)
- [X] T003 [P] Dependencias de Node en `package.json` (añadir `@clerk/vue`)
- [X] T004 [P] `.gitignore` con `.env`, `logs/`, `.venv`, `node_modules`, `dist`
- [X] T005 [P] Commitear `.env.example` con valores ficticios para Clerk y la IA
- [ ] T006 [P] Instalar y configurar Tailwind CSS en `vite.config.ts` y `src/style.css`

---

## Fase 2: Base común (bloquea las historias)

- [X] T007 Contrato Pydantic en `api/schemas.py` y TypeScript en `src/types/alcohol.ts`
- [X] T008 [P] Logger sin datos del usuario en `api/registro.py`
- [X] T009 Carga de `.env` y `GET /api/health` en `api/index.py`

**Punto de control**: base lista.

---

## Fase 3: Historia 1, estimar mi tasa (P1) 🎯 MVP

**Objetivo**: calcular y mostrar el resultado en una pantalla.

**Prueba independiente**: un cálculo válido muestra tasa, nivel, horas y aviso.

### Pruebas

- [X] T010 [P] [US1] Widmark, niveles y horas en `api/test_calculo.py`
- [X] T011 [P] [US1] Entrada válida con una sola llamada a la IA en `api/test_contrato.py`
- [X] T012 [P] [US1] Formulario y lista de bebidas en `tests/persona.spec.ts` y `tests/bebidas.spec.ts`

### Implementación

- [X] T013 [US1] Funciones puras de cálculo en `api/calculo.py`
- [X] T014 [US1] Cliente del LLM que solo explica en `api/ia.py`
- [X] T015 [US1] `POST /api/calcular` en `api/index.py`
- [X] T016 [P] [US1] Componentes `PersonaForm`, `BebidasLista`, `ResultadoPanel`, `ExplicacionPanel` en `src/components/`
- [X] T017 [US1] Servicio `src/services/api.ts` e integración en `src/App.vue`

---

## Fase 4: Historia 2, solo entra quien tiene sesión (P1)

**Objetivo**: Clerk en la SPA y verificación en FastAPI.

**Prueba independiente**: sin token o con token falso → 401 y la IA no se llama.

### Pruebas

- [ ] T018 [P] [US2] Prueba: sin cabecera `Authorization` → 401 y el mock de la IA no se llama, en `api/test_auth.py`
- [ ] T019 [P] [US2] Prueba: token inválido (simulando `authenticate_request` con `is_signed_in=False`) → 401 sin llamar a la IA, en `api/test_auth.py`
- [ ] T020 [P] [US2] Prueba: 11 peticiones en un minuto → la undécima da 429, en `api/test_auth.py`
- [ ] T021 [US2] Hacer que las pruebas existentes sustituyan `verificar_usuario` con `app.dependency_overrides` en `api/conftest.py`

### Implementación

- [X] T022 [US2] `clerkPlugin` en `src/main.ts` y botones `SignInButton`/`SignUpButton` en modal en `src/App.vue`
- [X] T023 [US2] Enviar `Authorization: Bearer <token>` desde `src/services/api.ts`
- [X] T024 [US2] `verificar_usuario` con `authenticate_request` y `authorized_parties` en `api/index.py`
- [X] T025 [US2] `limitar_usuario` (10/min, 50/día) en `api/index.py`
- [ ] T026 [US2] Eliminar `src/views/sign-in.vue`, `src/views/sign-up.vue` y la dependencia `vue-router` (principio I: sin rutas)
- [ ] T027 [US2] Responder 500, no 401, si faltan `CLERK_SECRET_KEY` o `FRONTEND_ORIGIN` en el servidor

---

## Fase 5: Historia 3, resultado aunque la IA falle (P2)

### Pruebas

- [X] T028 [P] [US3] Timeout, 401, 429, 500, JSON inválido y tasa absurda en `api/test_ia.py` y `api/test_contrato.py`
- [X] T029 [P] [US3] El log no contiene datos del usuario en `api/test_ia.py`

### Implementación

- [X] T030 [US3] `explicacion_generica` y `origen: "respaldo"` en `api/ia.py` y `api/index.py`

---

## Fase 6: Historia 4, errores comprensibles (P3)

- [X] T031 [P] [US4] 422 sin llamar a la IA en `api/test_contrato.py`
- [X] T032 [P] [US4] Error de red y reintento en `tests/bebidas.spec.ts`
- [X] T033 [US4] `ErrorCard.vue` y mensajes en `src/services/api.ts`
- [ ] T034 [US4] Mensajes propios para 401 ("Inicia sesión") y 429 ("Espera un minuto") en `src/services/api.ts`

---

## Fase 7: Contenedores y despliegue

- [X] T035 [P] `docker/backend.Dockerfile` con usuario sin privilegios y HEALTHCHECK
- [X] T036 [P] `docker/frontend.Dockerfile` y `docker/nginx.conf` con proxy `/api`
- [X] T037 `docker-compose.yml` con backend solo en red interna y secretos por `env_file`
- [X] T038 `docker-compose.aws.yml` y `docker/Caddyfile` con HTTPS
- [X] T039 [P] Terraform en `aws/terraform/` con SSH solo desde la IP de administración
- [X] T040 Commitear `docker/`, `docker-compose*.yml`, `.dockerignore` y `aws/` (la instancia clona el repo)
- [X] T041 `terraform apply`, desplegar con Compose y añadir el origen HTTPS en Clerk
- [X] T042 Rellenar la tabla de datos de despliegue en `aws/EC2.md`
- [X] T043 Corregir `.github/workflows/ci-cd.yml`: dejar solo las pruebas o desplegar en EC2; ahora construye un `Dockerfile` raíz que no existe

---

## Fase 8: Cierre

- [ ] T044 [P] Añadir al `ERS.md` los requisitos de Clerk (FR-007 a FR-009) y despliegue (NFR-005) con su trazabilidad a pruebas
- [ ] T045 [P] Documento de comparativa App 1 vs App 2 (tiempo, calidad, mantenibilidad, utilidad de la IA, esfuerzo de Clerk e infraestructura aparte)
- [ ] T046 Actualizar `README.md`: la IA ya no calcula la tasa, solo la explica
- [ ] T047 Ejecutar `quickstart.md` de principio a fin antes de la demo
- [ ] T048 `terraform destroy` después de la evaluación

---

## Dependencias

- Fase 2 bloquea las fases 3 a 6.
- T021 antes de ejecutar la batería de pytest completa con Clerk activo.
- T040 antes de T041 (la instancia clona el repositorio).
- T041 antes de T042 y de la demo.

## Trazabilidad requisito → prueba

| Requisito | Prueba |
|---|---|
| FR-001, FR-002 | T012, T031, `test_422_*`, `test_fuera_del_limite_*` |
| FR-003 | T010 |
| FR-004 | `tests/persona.spec.ts` (aviso y nivel), `tests/bebidas.spec.ts` (alerta peligrosa) |
| FR-005 | T011, T028 |
| FR-006 | T032 |
| FR-007, FR-008 | T018, T019 |
| FR-009 | T020 |
| NFR-001 | T029, `test_la_respuesta_no_expone_clave_ni_errores_internos` |
| NFR-005 | T041 (comprobación manual en la demo) |
