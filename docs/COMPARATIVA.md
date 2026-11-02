# Comparativa: App 1 (manual) frente a App 2 (Spec Kit + IA)

- **App 1:** la calculadora desarrollada a mano por el grupo y desplegada en Vercel. La IA calculaba la tasa y la explicaba.
- **App 2:** la misma aplicación, especificada con Spec Kit (`specs/001-taberna-app2/`) y desarrollada con ayuda de un asistente de IA. Añade acceso con Clerk, límite por usuario, contenedores y despliegue en EC2.

Los datos salen del historial de Git (`git log`). Lo que el repositorio no puede saber, como las horas reales o la opinión del grupo, queda marcado como pendiente.

## 1. Línea temporal

| Fase | Fechas (Git) | Autores en Git | Commits |
|---|---|---|---|
| App 1: base, frontend, API, cálculo e IA | 15/10/2026 | Daniel Mouimi, Manuel Palomares | 10 commits: `6e25605` a `a11e89f` |
| App 1: ERS y registro de errores | 19/10/2026 | Manolo1709, dmourom182 | `ab5b7b2`, `961f834`, `d176bd2` |
| Clerk (frontend, backend y pruebas) | 20/10/2026 a 29/10/2026 | dmourom182 | `050f0ea`, `27730bf`, `f4c2967`, `b139f3a` |
| App 2: Spec Kit (constitución, spec, plan, contrato y tareas) | 02/11/2026 | Manuel Palomares | `1c93867` |
| App 2: Docker Compose | 02/11/2026 | Manuel Palomares | `0e1fc67` |
| App 2: arreglo de la tasa, AWS, CI, pruebas de Clerk y documentación | 02/11/2026 | Manolo1709 | De `4375ac7` en adelante |

Los 10 commits de la App 1 tienen la misma hora (15/10/2026 13:41), así que el historial no sirve para medir cuánto se tardó en ella: se subió de una vez.

## 2. Tiempo (incluida la revisión)

| Medida | App 1 | App 2 |
|---|---|---|
| Días con commits | 2 (15/10 y 19/10), más 4 días de Clerk | 1 (02/11), más la especificación |
| Horas de desarrollo | _Pendiente: completar por el grupo_ | _Pendiente: completar por el grupo_ |
| Horas de revisión de lo generado | No aplica | _Pendiente: completar por el grupo_ |
| Horas de especificación (Spec Kit) | No aplica | _Pendiente: completar por el grupo_ |

## 3. Calidad y errores (mismos escenarios de aceptación)

Los escenarios son los criterios de aceptación de la ERS (CA-RF01 a CA-RF09) y los casos de cálculo E-01 a E-07.

| Escenario | App 1 | App 2 |
|---|---|---|
| Tasa correcta según Widmark (E-01 a E-07) | Correcta solo con la fórmula de respaldo. Con la IA, la tasa dependía del modelo. | Correcta siempre: la calcula el servidor. |
| Misma entrada, mismo resultado | No: la misma entrada dio 0,14, 0,30, 0,37 y 0,34 g/L en cuatro llamadas. | Sí: 0,35 g/L en las tres llamadas de prueba en producción. |
| Validación 422 sin llamar a la IA | Sí (`api/test_contrato.py`) | Sí |
| IA caída: resultado completo con `origen: "respaldo"` | Sí | Sí |
| Sin sesión: 401 sin llamar a la IA | No aplica (sin cuentas) | Sí (`api/test_auth.py`) |
| Límite por usuario: 429 en la petición 11 | No aplica | Sí (`test_undecima_peticion_en_un_minuto_devuelve_429`) |
| Pruebas automáticas | _Pendiente: completar por el grupo (número al cerrar la App 1)_ | 95 en el backend (cobertura del 95,8 %) y 22 en el frontend |
| Errores encontrados en la demo | _Pendiente: completar por el grupo_ | _Pendiente: completar por el grupo_ |

## 4. Mantenibilidad

| Aspecto | App 1 | App 2 |
|---|---|---|
| Dónde están las decisiones | README y ERS | Constitución, `spec.md`, `plan.md`, `research.md`, `tasks.md` y ERS 0.2 con trazabilidad a las pruebas |
| Estructura | `api/` (FastAPI) y `src/` (Vue) | Igual, más `docker/`, `docker-compose*.yml`, `aws/terraform/` y CI |
| Configuración del proveedor de IA | Variables de entorno | Igual. Cambiar de OpenRouter a Groq solo tocó el `.env`. |
| Despliegue | Vercel, automático desde Git | EC2 con Terraform y Compose. Actualizar es `git pull` y `docker compose up -d --build`. |
| Rutas en el frontend | Vistas `sign-in.vue` y `sign-up.vue` con `vue-router`, sin usar | Eliminadas: Clerk en ventana modal, una sola página |
| Valoración del grupo | _Pendiente: completar por el grupo_ | _Pendiente: completar por el grupo_ |

## 5. Utilidad de la IA

### Propuestas aceptadas

- **La tasa la calcula el servidor y la IA solo la explica.** Se detectó al medir la latencia en producción: la misma entrada daba tasas distintas en cada llamada. El código ya calculaba con Widmark en local, pero no se había desplegado.
- **Cambio de proveedor a Groq.** El modelo gratuito de OpenRouter que se usaba dejó de estar disponible. Se comprobaron los límites reales de Groq con las cabeceras de una petición (1000 peticiones al día y 8000 tokens por minuto) y la latencia (0,5 a 1 s por cálculo).
- **Contador del límite por usuario entre pruebas.** Al añadir `test_contrato.py`, 16 pruebas fallaban con 429 porque el contador de `limitar_usuario` se compartía entre pruebas. Se reinicia en `api/conftest.py`.
- **Pruebas de Clerk según la especificación.** `test_auth.py` se movió a `api/`. Ahora comprueba que la IA no se llama con 401 y que la petición 11 da 429. Las demás pruebas sustituyen `verificar_usuario` con `dependency_overrides`.
- **CI solo con pruebas.** El workflow generado construía un `Dockerfile` raíz que no existe y desplegaba en ECR, ECS y App Runner, que no se usan. Se dejó solo el trabajo de pruebas.
- **Correcciones en la infraestructura:** el ID de la AMI de Canonical que se propuso era incorrecto y se corrigió, y la descripción del grupo de seguridad tenía un apóstrofo que AWS no admite.

### Propuestas rechazadas o corregidas

- **Tailwind CSS:** el plan lo incluía (T006), pero el grupo lo descartó porque no es obligatorio y la interfaz ya tenía CSS propio.
- **Despliegue con ECR, ECS y App Runner** en el CI: rechazado; el despliegue es en EC2 con Compose.
- Otras propuestas descartadas por el grupo: _Pendiente: completar por el grupo_

### Valoración

| Pregunta | Respuesta |
|---|---|
| ¿Qué porcentaje de lo propuesto se aceptó sin cambios? | _Pendiente: completar por el grupo_ |
| ¿Dónde ahorró más tiempo? | _Pendiente: completar por el grupo_ |
| ¿Dónde hizo perder tiempo? | _Pendiente: completar por el grupo_ |

## 6. Esfuerzo de Clerk e infraestructura, por separado

| Parte | Trabajo | Commits | Tiempo |
|---|---|---|---|
| Clerk | Plugin en Vue, botones modales, token en cada petición, verificación con `authenticate_request`, límite por usuario y pruebas | `050f0ea`, `27730bf`, `f4c2967`, `b139f3a`, `4489c54`, `ccb342a` | _Pendiente: completar por el grupo_ |
| Contenedores | Dockerfiles de backend y frontend, nginx, Compose con red interna y Caddy con HTTPS | `0e1fc67` | _Pendiente: completar por el grupo_ |
| AWS | Terraform (clave SSH, grupo de seguridad, instancia, IP elástica), `user-data.sh`, dominio propio y guía `aws/EC2.md` | `88f714b` | _Pendiente: completar por el grupo_ |
| CI | GitHub Actions con pruebas y typecheck | `04e2f2b`, `42e2e42` | _Pendiente: completar por el grupo_ |

## 7. Conclusión

_Pendiente: completar por el grupo._
