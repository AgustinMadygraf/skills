---
name: skill-frontend-orchestrator
description: "Orquestador frontend que coordina auditorias y ejecucion de tareas para Vue/TypeScript. Ejecuta frontend-best-practices-audit, clean-architecture-orchestrator (como capa general), frontend-testing-vue-ts-tailwind y todo-workflow, consolidando resultados en docs/todo.md."
---


# Skill Frontend Orchestrator

Coordina el flujo frontend completo con foco en bajo riesgo y trazabilidad.

## Cuando usar

Usar cuando el usuario pida:
- orquestar trabajo frontend de punta a punta
- correr auditorias frontend + seguridad general
- procesar backlog tecnico frontend en `docs/todo.md`

## Flujo

1. Analizar contexto y alcance del cambio frontend.
2. Ejecutar auditorias relevantes:
- `frontend-best-practices-audit` para Vue/TS/UI.
- `clean-architecture-orchestrator` para arquitectura/SOLID/seguridad general.
3. Si aplica, ejecutar `frontend-testing-vue-ts-tailwind`.
4. Consolidar tareas accionables en `docs/todo.md`.
5. Ejecutar `todo-workflow` para tareas de bajo riesgo.
6. Escalar solo dudas de alto impacto a `docs/decision/questions.md`.
7. Cerrar con resumen de cambios, riesgos y pendientes.

## Reglas de decision

- Resolver autonomamente cambios mecanicos y reversibles.
- Escalar decisiones cross-cutting o con impacto de producto.
- No reemplaza skills especialistas; los coordina.
- Estandarizar salida en `docs/todo.md` usando `../shared/references/hallazgo-template.md`.

## Integracion

- `frontend-best-practices-audit`
- `clean-architecture-orchestrator`
- `frontend-testing-vue-ts-tailwind`
- `todo-workflow`
- `decision-helper` (solo cuando corresponda)

## Referencias externas

- `../shared/references/hallazgo-template.md`
- `../shared/references/severidad-matriz.md`
- `../shared/references/decision-escalation-rules.md`
- `../shared/config/todo-output-schema.yaml`

