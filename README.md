# Calculadora de nivel de alcohol en sangre

## Idea

Aplicación web que estima cómo de borracho va una persona. El usuario indica qué bebidas ha ingerido, su peso corporal, su sexo biológico, el tiempo transcurrido desde que empezó a beber y cómo de lleno tiene el estómago. La aplicación calcula una tasa de alcohol en sangre aproximada y la traduce a un nivel comprensible.

## Objetivo de la primera versión

Permitir que una persona registre lo que ha bebido y obtenga una estimación sencilla de su tasa de alcohol en sangre (TAS) y de cuánto tardará en bajar. El resultado es solo orientativo: la aplicación no puede garantizar que una persona esté en condiciones de conducir ni sustituye a un alcoholímetro.

## Datos del formulario

Para cada bebida:

- Tipo de bebida, por ejemplo cerveza, vino, licor o cóctel.
- Volumen en ml o número de unidades (caña, copa, chupito).
- Graduación alcohólica (% vol.), con un valor por defecto según el tipo de bebida.
- Cantidad.

Datos de la persona:

- Peso corporal en kg.
- Sexo biológico (hombre o mujer), porque cambia el reparto del alcohol en el cuerpo.
- Tiempo transcurrido desde la primera bebida.
- Nivel de llenado del estómago: vacío, algo de comida o lleno.

## Resultado esperado

La aplicación muestra:

- La tasa de alcohol en sangre estimada (g/L).
- Un nivel de embriaguez en lenguaje sencillo: sobrio, algo alegre, borracho o peligroso.
- Una estimación del tiempo que tardará en volver a 0,0 g/L.
- Un aviso de que no se debe conducir si se ha bebido, con independencia del resultado.
- Una advertencia destacada cuando la tasa estimada sea alta, con recomendación de dejar de beber y pedir ayuda si hay síntomas graves.

## Reglas iniciales

1. Calcular los gramos de alcohol de cada bebida a partir del volumen, la graduación y la densidad del alcohol (0,8 g/ml).
2. Estimar la tasa con la fórmula de Widmark: gramos de alcohol / (peso en kg × coeficiente de distribución), con un coeficiente aproximado de 0,68 para hombres y 0,55 para mujeres.
3. Restar la eliminación por el paso del tiempo, con una tasa media aproximada de 0,15 g/L por hora.
4. Ajustar la absorción según el estómago: más lenta y con un pico menor si hay comida, más rápida si está vacío.
5. Nunca mostrar una tasa negativa; el mínimo es 0,0 g/L.
6. Presentar siempre el resultado como una estimación aproximada, nunca como un valor exacto.

## Flujo de uso

1. El usuario introduce sus datos personales: peso, sexo biológico y estómago.
2. Añade las bebidas que ha tomado y el tiempo transcurrido.
3. La aplicación valida que haya peso, sexo y al menos una bebida.
4. La lógica calcula la tasa estimada y el nivel de embriaguez.
5. Se muestra el resultado con su explicación y los avisos de seguridad.
6. El usuario puede volver al formulario y modificar los datos.

## Fuera del alcance inicial

- Medir el alcohol real mediante sensores o un alcoholímetro.
- Determinar si una persona puede conducir o está dentro del límite legal.
- Tener en cuenta medicación, enfermedades, tolerancia individual o el consumo de otras sustancias.
- Guardar historiales o cuentas de usuario.
- Usar inteligencia artificial para tomar decisiones de seguridad. La IA calcula la tasa siguiendo la fórmula de Widmark, pero el nivel y los avisos salen de reglas explícitas, y si la IA falla se usa la fórmula.

## Criterio de éxito

Con distintas combinaciones de bebidas, peso, sexo, tiempo y estómago, la página devuelve una tasa estimada coherente, explica el nivel de embriaguez y deja claro que es una aproximación y que no se debe conducir tras beber.
