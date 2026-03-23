---
name: 2b-architecture-refactor-assistant
description: "Asistente de refactor arquitectonico guiado para resolver hallazgos de layer-boundary sin autofix ciego."
---

# Architecture Refactor Assistant

Skill para ejecutar refactors arquitectonicos de manera explicita y segura.

## Activacion

- Uso explicito unicamente: `$2b-architecture-refactor-assistant`.

## Objetivo

- Tomar hallazgos de `docs/todo.md` (especialmente `layer-boundary`).
- Proponer refactor por lotes pequenos con impacto acotado.
- Aplicar cambios solo con trazabilidad y validacion posterior.

## Comando recomendado

```bash
python ~/.codex/skills/2b-architecture-refactor-assistant/scripts/generate_refactor_plan.py --repo-root .
```

Salida principal:

- `docs/refactor/architecture-refactor-plan.md`

## Sugerencias de patch (sin aplicar)

```bash
python ~/.codex/skills/2b-architecture-refactor-assistant/scripts/generate_patch_suggestions.py --repo-root .
```

Salida principal:

- `docs/refactor/architecture-patch-suggestions.md`

## Decidir que crear ahora

```bash
python ~/.codex/skills/2b-architecture-refactor-assistant/scripts/decide_layer.py --repo-root . --change "descripcion del cambio"
```

Salida:

- capa recomendada (`entities`, `use_cases`, `gateways`, `controllers`, `presenters`, `infrastructure`)
- ruta sugerida
- dependencias permitidas/prohibidas

## Reglas

- No hacer autofix masivo ciego.
- No cambiar comportamiento funcional sin justificar.
- Priorizar mover dependencias hacia puertos/adapters correctos.
- Luego del refactor, re-ejecutar:
  - `$1a-project-structure-gate`
  - `$2a-project-architecture-gate`
