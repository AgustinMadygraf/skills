---
name: skill-backend-orchestrator
description: "Orquestador backend para Python/FastAPI. Coordina auditoria backend, testing backend, clean-architecture-orchestrator general y todo-workflow, consolidando backlog tecnico en docs/todo.md."
---


# Skill Backend Orchestrator

Orquesta flujo backend end-to-end con foco en seguridad API, performance y calidad de pruebas.

## Cuando usar

Usar cuando el usuario pida:
- coordinar analisis y ejecucion de tareas backend
- auditar backend FastAPI y convertir hallazgos en plan accionable
- fortalecer o reparar cobertura de testing backend (unit, API/DB integration, contract y performance smoke)

## Flujo

1. Delimitar alcance backend en `src/`.
2. Ejecutar `skill-backend-code-audit`.
3. Ejecutar `clean-architecture-orchestrator` para capa general (arquitectura/SOLID/seguridad transversal).
4. Ejecutar `skill-backend-testing` si hay cambios funcionales o brechas de pruebas, cubriendo unit, API/DB integration, contract y performance smoke.
5. Consolidar tareas en `docs/todo.md`.
6. Ejecutar `todo-workflow` para certezas y dudas de bajo nivel.
7. Escalar solo decisiones de alto impacto a `decision-helper`.

## Reglas de autonomia

- Resolver cambios mecanicos y de bajo riesgo sin interrumpir.
- Escalar decisiones de arquitectura o cambios cross-cutting.
- No suplantar skills especialistas; coordinarlos.
- Estandarizar salida en `docs/todo.md` usando `../shared/references/hallazgo-template.md`.

## Integracion

- `skill-backend-code-audit`
- `skill-backend-testing`
- `clean-architecture-orchestrator`
- `todo-workflow`
- `decision-helper` (si aplica)

## Referencias externas

- `../shared/references/hallazgo-template.md`
- `../shared/references/severidad-matriz.md`
- `../shared/references/decision-escalation-rules.md`
- `../shared/config/todo-output-schema.yaml`

