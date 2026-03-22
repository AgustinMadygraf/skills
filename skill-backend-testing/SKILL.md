---
name: skill-backend-testing
description: "Skill de testing backend Python para FastAPI. Cubre unit, integracion API/DB, contract tests y performance smoke con pytest. Registra resultado y pendientes en docs/todo.md."
---


# Skill Backend Testing

Testing especializado para backend `Python + FastAPI`.

## Alcance por defecto
Si el pedido es de testing en Python/FastAPI, este skill tiene precedencia sobre `testing-general`.

- Unit tests de logica de dominio y servicios.
- Integration tests de endpoints FastAPI (request/response, validaciones, errores y auth basica).
- Integration tests de DB (repositorios, consultas y transacciones relevantes).
- Contract tests de API (schema y compatibilidad de contratos).
- Performance smoke tests (deteccion temprana de regresiones de latencia basica).
- Excluye e2e multi-servicio por defecto (solo si el usuario lo pide).

## Stack recomendado

- `pytest`
- `pytest-asyncio` (cuando haya endpoints o servicios async)
- `httpx` con `AsyncClient` para pruebas de API
- `pytest-cov` para cobertura
- Herramientas de apoyo segun contexto: `testcontainers` o DB local de prueba, `schemathesis` o validadores OpenAPI, y `pytest-benchmark` o medicion equivalente para smoke performance.

## Reglas

- Priorizar pruebas de alto valor y bajo acoplamiento.
- Evitar tests fragiles atados a detalles internos.
- Cada analisis o ejecucion debe reflejarse en `docs/todo.md`.
- Formatear hallazgos con `../shared/references/hallazgo-template.md`.

## Umbrales por defecto para performance smoke

- `GET` criticos: `p95 <= 300 ms`.
- `POST/PUT/PATCH/DELETE` criticos: `p95 <= 500 ms`.
- Error rate en smoke: `< 1%`.
- Regresion permitida contra baseline reciente: `<= 20%` en p95.
- Si no hay baseline, usar los valores absolutos anteriores y dejar tarea de calibracion en `docs/todo.md`.
- Configuracion machine-readable: `../shared/config/backend-performance-smoke.yaml`.

## Flujo minimo

1. Identificar riesgo funcional principal del cambio backend.
2. Disenar matriz minima de casos:
- camino feliz
- errores esperados
- validaciones de entrada
- permisos/autorizacion basica (si aplica)
- persistencia y consistencia en DB
- compatibilidad de contrato API
- umbral de latencia para smoke performance
3. Implementar o corregir tests con fixtures reutilizables.
4. Ejecutar pruebas objetivo y reportar resultado.
5. Registrar gaps de test y acciones sugeridas en `docs/todo.md`.

## Integracion

- `testing-general` para estrategia transversal.
- `skill-backend-orchestrator` para coordinacion completa.
- `todo-workflow` para ejecucion de tareas de testing de bajo riesgo.

## Referencias externas

- `../shared/references/hallazgo-template.md`
- `../shared/references/severidad-matriz.md`
- `../shared/config/backend-performance-smoke.yaml`
- `../shared/config/todo-output-schema.yaml`

