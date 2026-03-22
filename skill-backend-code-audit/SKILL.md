---
name: skill-backend-code-audit
description: "Auditoria especializada de backend Python/FastAPI en src/. Evalua seguridad de APIs y performance; deja hallazgos accionables en docs/todo.md sin aplicar fixes automaticos."
---


# Skill Backend Code Audit

Auditoria preventiva para backend en `Python + FastAPI`.

## Alcance
Para auditorias backend Python/FastAPI, este skill tiene precedencia sobre `clean-architecture-orchestrator`.

- Solo analiza `src/`.
- Incluye:
- seguridad de API (authn/authz, CORS, manejo de secretos, validacion de input, manejo de errores, hardening basico, rate limiting cuando aplique)
- performance (patrones async/sync, N+1, uso de I/O bloqueante, cacheo y consultas costosas evidentes)
- Excluye:
- Clean Architecture y SOLID (capa general: `clean-architecture-orchestrator`)

## Regla operativa

- No aplicar fixes automaticos.
- Escribir hallazgos claros y accionables en `docs/todo.md`.
- Priorizar hallazgos por severidad: critica, alta, media, baja.
- Usar formato comun de hallazgos en `../shared/references/hallazgo-template.md`.

## Flujo minimo

1. Recorrer `src/` y mapear endpoints, dependencias y capas de acceso a datos.
2. Detectar riesgos de seguridad de API y anti-patrones de performance.
3. Registrar cada hallazgo con:
- ubicacion (archivo)
- riesgo
- impacto
- recomendacion concreta
4. Consolidar resultados en `docs/todo.md`.

## Integracion

- `clean-architecture-orchestrator` para arquitectura/SOLID y controles generales.
- `skill-backend-orchestrator` para ejecucion end-to-end.
- `todo-workflow` para procesar tareas de bajo riesgo.

## Referencias externas

- `../shared/references/hallazgo-template.md`
- `../shared/references/severidad-matriz.md`
- `../shared/config/todo-output-schema.yaml`

