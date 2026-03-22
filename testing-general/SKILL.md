---
name: testing-general
description: "Skill generalista para dise\u00f1ar, ampliar, depurar y ejecutar estrategias de testing en cualquier stack. Se usa cuando el usuario pide crear tests, mejorar cobertura, diagnosticar fallos, definir pir\u00e1mide de pruebas, revisar calidad de suites o decidir qu\u00e9 nivel de test conviene. Prioriza pruebas de alto valor, minimiza fragilidad y deja claros riesgos, supuestos y gaps. El resultado del an\u00e1lisis debe registrarse en docs/todo.md como tareas accionables."
---


# Testing General

Skill para trabajo de testing transversal, independiente del framework.

## Cu\u00e1ndo usarlo

Usar este skill cuando el usuario pida cualquiera de estas tareas:

- Crear o ampliar tests.
- Mejorar cobertura sin inflarla artificialmente.
- Diagnosticar tests inestables o fallando.
- Dise\u00f1ar estrategia de testing para una feature.
- Decidir entre unit, integration, e2e, contract o smoke tests.
- Revisar calidad, duplicaci\u00f3n o fragilidad de la suite actual.

Si el pedido es claramente de frontend Vue + TypeScript + Tailwind, preferir `frontend-testing-vue-ts-tailwind`.
Si el pedido es claramente de backend Python/FastAPI, preferir `skill-backend-testing`.

## Objetivo

Maximizar confianza con el menor costo de mantenimiento posible.

## Modo de operacion

Este skill debe dejar un resultado operativo en `docs/todo.md`.

- Si se usa para auditoria o diagnostico: registrar hallazgos, gaps y acciones recomendadas en `docs/todo.md`.
- Si se usa para ejecutar cambios concretos: registrar en `docs/todo.md` las tareas remanentes, riesgos residuales o siguientes pasos detectados.
- No cerrar el trabajo solo con un mensaje en chat si existen acciones pendientes relevantes.

El skill debe:

1. Identificar el comportamiento cr\u00edtico.
2. Elegir el nivel de prueba correcto.
3. Implementar o ajustar tests con foco en riesgo real.
4. Ejecutar verificaciones relevantes.
5. Reportar cobertura efectiva, riesgos residuales y siguientes pasos.

## Flujo de trabajo

### 1. Entender el cambio o riesgo

Antes de escribir tests:

- Leer el c\u00f3digo afectado y los tests cercanos.
- Detectar entradas, salidas, efectos colaterales y dependencias.
- Separar l\u00f3gica pura, integraciones, IO y comportamiento observable.
- Identificar regresiones plausibles, no solo caminos felices.

### 2. Elegir el nivel de test

Aplicar esta heur\u00edstica:

- `unit`: l\u00f3gica determinista, validaciones, mapeos, reglas de negocio.
- `integration`: colaboraci\u00f3n entre m\u00f3dulos, repositorios, gateways, adapters.
- `contract`: shape y sem\u00e1ntica de interfaces entre capas o servicios.
- `e2e` o `smoke`: flujos cr\u00edticos para el usuario, navegaci\u00f3n, wiring real.

Evitar e2e cuando un unit o integration test capture el riesgo con menos fragilidad.
Evitar unit tests que solo reafirman implementaciones triviales.

### 3. Dise\u00f1ar casos \u00fatiles

Cubrir primero:

- camino feliz,
- validaciones y bordes,
- errores esperables,
- comportamiento ante dependencias fallidas,
- regresiones conocidas o muy probables.

No perseguir cobertura de l\u00ednea como objetivo primario.
Preferir pocos casos con alta se\u00f1al antes que muchas pruebas repetitivas.

### 4. Implementar con baja fragilidad

Reglas:

- Testear comportamiento observable, no detalles internos.
- Mockear solo el borde necesario.
- Mantener fixtures peque\u00f1os y expl\u00edcitos.
- Evitar sleeps, temporizadores arbitrarios y acoplamiento a orden incidental.
- Si un test necesita demasiados mocks, probablemente el nivel de test es incorrecto o el dise\u00f1o est\u00e1 demasiado acoplado.

### 5. Ejecutar y depurar

Al correr tests:

- Empezar por el subconjunto m\u00e1s chico relevante.
- Si fallan, distinguir entre bug real, expectativa incorrecta o test fr\u00e1gil.
- Corregir la causa, no maquillar el s\u00edntoma.
- Si aparece deuda de dise\u00f1o que bloquea buen testing, dejarla expl\u00edcita.

### 6. Cerrar con evidencia

Informar:

- qu\u00e9 se cubri\u00f3,
- qu\u00e9 riesgo queda fuera,
- qu\u00e9 comandos se ejecutaron,
- qu\u00e9 tests nuevos o modificados se agregaron,
- si hace falta ampliar cobertura en una siguiente iteraci\u00f3n.
- y reflejar en `docs/todo.md` las tareas pendientes resultantes.

## Heur\u00edsticas de calidad

Una buena suite:

- falla cuando el comportamiento rompe,
- no falla por refactors seguros,
- se lee como especificaci\u00f3n breve,
- minimiza setup innecesario,
- corre r\u00e1pido en el nivel adecuado.

Se\u00f1ales de problema:

- exceso de mocks,
- snapshots grandes sin criterio,
- asserts sobre implementaci\u00f3n privada,
- dependencia de orden global,
- tests largos con varios comportamientos no relacionados,
- reintentos para ocultar flakiness.

## Patr\u00f3n de respuesta

Cuando este skill se active:

1. Resumir el riesgo principal que se quiere cubrir.
2. Explicar qu\u00e9 nivel de test se va a usar y por qu\u00e9.
3. Implementar o ajustar tests.
4. Ejecutar validaciones relevantes.
5. Actualizar `docs/todo.md` con pendientes, gaps o follow-ups.
6. Reportar hallazgos, evidencia y riesgos remanentes.

## Formato esperado en docs/todo.md

Registrar tareas concretas, verificables y orientadas a riesgo. Ejemplos:

- [ ] Agregar unit tests para validaciones de `leadWizard` cubriendo bordes de email, comentario y telefono
- [ ] Agregar tests de integracion para `QuotePage.vue` cubriendo 422, 429 y descarga de PDF
- [ ] Revisar y corregir flakiness o ruido de consola que afecta la ejecucion estable de Vitest

