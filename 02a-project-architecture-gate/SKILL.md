---
name: 02a-project-architecture-gate
description: "Gate estricto de arquitectura: layer-boundary/import-boundary con severidades."
---

# Project Architecture Gate

Valida fronteras de arquitectura limpia por capas.

## Activacion

- Uso explicito unicamente: `$02a-project-architecture-gate`.

## Comando

```bash
python ~/.codex/skills/01-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check
```

## Prevencion de regresiones

1. Crear baseline inicial:

```bash
python ~/.codex/skills/01-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --write-architecture-baseline
```

2. Enforzar baseline en corridas futuras:

```bash
python ~/.codex/skills/01-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --enforce-architecture-baseline
```

## Gate

- Falla con codigo != 0 si existen hallazgos `critical`.
- `presenters_imports_controllers` se considera `critical`.
- Falla con codigo != 0 si hay hallazgos nuevos respecto del baseline (cuando `--enforce-architecture-baseline` esta activo).
- `warning/info` se reportan en `docs/todo.md`.
