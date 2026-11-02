# Especificación de la funcionalidad: La Taberna, calculadora de alcohol en sangre con acceso autenticado

**Rama de la funcionalidad**: `001-taberna-app2`

**Creada**: 2026-11-02

**Estado**: Borrador para revisión del grupo

**Entrada**: Descripción del grupo: "Una mini aplicación web de una sola pantalla en la que una persona con sesión iniciada indica qué ha bebido, su peso, su sexo, el tiempo que lleva bebiendo y cómo tiene el estómago, y obtiene una estimación de su tasa de alcohol en sangre, un nivel de embriaguez, el tiempo hasta volver a 0,0 g/L, una explicación sencilla y avisos de seguridad. Misma función y contrato que la App 1, añadiendo acceso con cuenta y despliegue en contenedores."

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1: Estimar mi tasa de alcohol (Prioridad: P1)

Una persona con sesión iniciada rellena sus datos y las bebidas que ha tomado, pulsa calcular y, en la misma pantalla, ve su tasa estimada, su nivel de embriaguez, las horas hasta volver a 0,0 g/L, una explicación en lenguaje sencillo, unos consejos y el aviso de no conducir.

**Por qué esta prioridad**: es la única función de la aplicación; sin ella no hay producto.

**Prueba independiente**: con la sesión iniciada, enviar 70 kg, hombre, 1 h, estómago con algo de comida y 2 cañas de 330 ml al 5 %, y comprobar que la pantalla muestra una tasa coherente con Widmark, su nivel, las horas hasta cero y el aviso de conducción.

**Escenarios de aceptación**:

1. **Dado** un usuario con sesión iniciada y datos válidos, **cuando** pulsa calcular, **entonces** ve un indicador de espera y después la tasa (g/L, dos decimales), el nivel, las horas hasta 0,0 g/L, la explicación, los consejos y el aviso de no conducir.
2. **Dado** un resultado de nivel "peligroso", **cuando** se muestra, **entonces** aparece una alerta destacada que recomienda dejar de beber y llamar al 112 si hay síntomas graves.
3. **Dado** un resultado ya mostrado, **cuando** el usuario cambia los datos y vuelve a calcular, **entonces** el resultado se sustituye sin recargar la página ni guardar nada.

---

### Historia de usuario 2: Solo entra quien tiene sesión (Prioridad: P1)

La aplicación solo calcula para usuarios autenticados. Quien no ha iniciado sesión ve la invitación a entrar o registrarse en una ventana modal, sin salir de la pantalla. El servidor rechaza cualquier petición sin una sesión válida antes de gastar una llamada a la IA.

**Por qué esta prioridad**: protege la clave de la IA y el crédito del proveedor frente a abusos; es un requisito de la App 2.

**Prueba independiente**: hacer una petición al cálculo sin token y otra con un token inventado, y comprobar que ambas devuelven 401 y que la IA no se ha llamado.

**Escenarios de aceptación**:

1. **Dado** un visitante sin sesión, **cuando** abre la aplicación, **entonces** ve los botones de iniciar sesión y registrarse, que abren un modal en la misma pantalla.
2. **Dado** una petición de cálculo sin token, **cuando** llega al servidor, **entonces** responde 401 y no llama a la IA.
3. **Dado** una petición con un token caducado, manipulado o emitido para otro origen, **cuando** llega al servidor, **entonces** responde 401 y no llama a la IA.
4. **Dado** un usuario que supera 10 cálculos por minuto o 50 al día, **cuando** envía otro, **entonces** recibe 429 y un mensaje claro.

---

### Historia de usuario 3: Obtener resultado aunque la IA falle (Prioridad: P2)

Si el proveedor de IA no responde, tarda demasiado o devuelve algo inválido, el usuario sigue recibiendo la tasa, el nivel y unos consejos genéricos.

**Por qué esta prioridad**: el resultado de seguridad no puede depender de un servicio externo gratuito.

**Prueba independiente**: con la IA simulada fallando (timeout, 401, 429, 500, JSON inválido), comprobar que la respuesta es completa y marca `origen: "respaldo"`.

**Escenarios de aceptación**:

1. **Dado** que la IA agota el tiempo de espera (30 s), **cuando** se calcula, **entonces** se devuelve el resultado con explicación genérica y `origen: "respaldo"`.
2. **Dado** que la IA devuelve un texto que no cumple el esquema, **cuando** se calcula, **entonces** se descarta y se usa la explicación genérica.
3. **Dado** cualquier fallo de la IA, **cuando** se registra, **entonces** el log solo contiene el motivo, nunca los datos del usuario, la clave ni la respuesta de la IA.

---

### Historia de usuario 4: Errores comprensibles y reintento (Prioridad: P3)

Si los datos no son válidos o el servidor no responde, el usuario ve un mensaje claro en la misma pantalla y puede corregir y volver a intentarlo.

**Por qué esta prioridad**: mejora la experiencia, pero no afecta al cálculo.

**Prueba independiente**: enviar un peso fuera de rango y, por separado, simular el servidor caído; comprobar el mensaje y que el botón permite reintentar.

**Escenarios de aceptación**:

1. **Dado** un dato fuera de límites, **cuando** se envía, **entonces** el servidor responde 422 sin llamar a la IA y la pantalla muestra "Hay datos que no son válidos".
2. **Dado** que no hay conexión, **cuando** se envía, **entonces** se muestra un mensaje de red y se puede reintentar.
3. **Dado** un 401 o un 429, **cuando** se recibe, **entonces** se muestra un mensaje específico (iniciar sesión o esperar), no un código numérico.

### Casos límite

- Peso exactamente 30 o 250 kg, 0 o 24 horas, 1 o 50 bebidas: se aceptan.
- Peso 29 o 251, 25 horas, 0 o 51 bebidas, graduación negativa o mayor que 100: 422 sin llamar a la IA.
- Cuerpo vacío, no JSON o campos ausentes: 422.
- Mucho tiempo transcurrido: la tasa nunca es negativa; se muestra 0,0 g/L y "ya estás a 0".
- La IA devuelve una tasa absurda (más de 6 g/L): se descarta su salida.
- Variables de Clerk ausentes en el servidor: el servidor no debe aceptar ninguna petición.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: El sistema DEBE ofrecer un único formulario con peso, sexo biológico, horas bebiendo, estado del estómago y una lista de una a cincuenta bebidas (tipo, volumen, graduación y cantidad). *(ERS RF-01)*
- **FR-002**: El sistema DEBE validar todos los datos con los límites de la sección de casos límite y rechazar con 422 los inválidos sin llamar a la IA. *(ERS RF-02)*
- **FR-003**: El sistema DEBE calcular la tasa con la fórmula de Widmark, el factor de estómago y la eliminación de 0,15 g/L por hora, con un mínimo de 0,0 g/L, y clasificarla en sobrio, alegre, borracho o peligroso. *(ERS RF-03)*
- **FR-004**: El sistema DEBE mostrar en la misma pantalla la tasa, el nivel, las horas hasta 0,0 g/L, el aviso de no conducir y que es una estimación, y una alerta destacada si el nivel es peligroso. *(ERS RF-04)*
- **FR-005**: El sistema DEBE pedir a un proveedor de IA una explicación y consejos personalizados, enviándole solo números y valores cerrados, y usar un texto genérico si la IA falla. *(ERS RF-05)*
- **FR-006**: El sistema DEBE mostrar mensajes de error comprensibles y permitir reintentar. *(ERS RF-06)*
- **FR-007**: El sistema DEBE exigir una sesión válida de Clerk para calcular; el inicio de sesión y el registro se hacen en un modal dentro de la misma pantalla. *(nuevo en App 2)*
- **FR-008**: El servidor DEBE verificar el token de sesión y su origen antes de llamar a la IA y responder 401 si falta o no es válido. *(nuevo en App 2)*
- **FR-009**: El servidor DEBE limitar a cada usuario a 10 cálculos por minuto y 50 al día, respondiendo 429 al superarlo. *(nuevo en App 2)*
- **FR-010**: El sistema NO DEBE guardar entradas, resultados ni historiales.

### Requisitos no funcionales

- **NFR-001**: La clave de la IA y la clave secreta de Clerk solo existen en el servidor; no aparecen en Git, en las imágenes, en el frontend, en las respuestas ni en los logs. *(ERS RNF-01)*
- **NFR-002**: La espera máxima a la IA es de 30 s; con el respaldo, el servidor responde en 1 s o menos en el 95 % de los casos. *(ERS RNF-02)*
- **NFR-003**: Todos los campos tienen etiqueta y son usables con teclado; el resultado y los errores se anuncian a lectores de pantalla; funciona a 360 px sin desplazamiento horizontal. *(ERS RNF-03)*
- **NFR-004**: Toda la lógica tiene pruebas automáticas con la IA simulada. *(ERS RNF-04)*
- **NFR-005**: La aplicación se despliega con dos contenedores en una instancia Linux, accesible solo por HTTPS, con los puertos mínimos y el SSH limitado a la IP de administración. *(nuevo en App 2)*

### Entidades clave

- **Persona**: peso, sexo, horas bebiendo y estómago. Solo existe durante la petición.
- **Bebida**: tipo, volumen, graduación y cantidad.
- **Solicitud de cálculo**: una persona y su lista de bebidas.
- **Resultado**: tasa, nivel, horas hasta cero, explicación, consejos, aviso de conducción y origen (ia o respaldo).
- **Sesión**: token emitido por Clerk que identifica al usuario; no se guarda en el servidor.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: En los casos de prueba, la tasa coincide con el cálculo manual de Widmark con una tolerancia de ±0,05 g/L.
- **SC-002**: El 100 % de los resultados muestra el aviso de no conducir.
- **SC-003**: El 100 % de las peticiones sin token o con token inválido recibe 401 y ninguna llega a la IA.
- **SC-004**: Con la IA caída, el 100 % de las peticiones válidas devuelve un resultado completo.
- **SC-005**: Un usuario sin experiencia completa un cálculo, incluido el inicio de sesión, en menos de 2 minutos.
- **SC-006**: La aplicación responde por HTTPS en la URL pública de EC2 durante la demostración.

## Suposiciones

- El usuario introduce datos veraces; la estimación es orientativa y no sustituye a un alcoholímetro.
- Los coeficientes 0,68 y 0,55 y la eliminación de 0,15 g/L por hora son aceptables para una estimación.
- El plan gratuito del proveedor de IA y de Clerk basta para el uso académico.
- El límite de peticiones se guarda en memoria del proceso, válido para una sola instancia.
- La App 2 mantiene la misma función y el mismo contrato JSON que la App 1.
