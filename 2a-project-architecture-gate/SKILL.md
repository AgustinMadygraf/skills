---
name: 2a-project-architecture-gate
description: "Gate estricto de arquitectura: layer-boundary/import-boundary + solid-lite (SRP/DIP/ISP) con severidades."
---

# Project Architecture Gate

Valida fronteras de arquitectura limpia por capas y un set SOLID-lite.

## Activacion

- Uso explicito unicamente: `$2a-project-architecture-gate`.

## Comando

```bash
python ~/.codex/skills/1-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check
```

## Prevencion de regresiones

1. Crear baseline inicial:

```bash
python ~/.codex/skills/1-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --write-architecture-baseline
```

2. Enforzar baseline en corridas futuras:

```bash
python ~/.codex/skills/1-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --enforce-architecture-baseline
```

## Calibracion solid-lite

Archivo de configuracion (opcional):

- `docs/architecture/solid-thresholds.json`

Claves soportadas:

- `max_use_case_classes_per_module`
- `max_use_case_top_level_functions`
- `max_gateway_public_methods`
- `max_public_methods_per_class`

Override de ruta:

```bash
python ~/.codex/skills/1-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --solid-thresholds docs/architecture/solid-thresholds.json
```

## Gate

- Falla con codigo != 0 si existen hallazgos `critical`.
- `presenters_imports_controllers` se considera `critical`.
- Incluye `solid-lite`:
  - SRP-lite (modulos/clases demasiado cargados)
  - DIP-lite (imports de vendors en capas internas y uso sospechoso de concretos)
  - ISP-lite (interfaces gateway demasiado grandes)
- Falla con codigo != 0 si hay hallazgos nuevos respecto del baseline (cuando `--enforce-architecture-baseline` esta activo).
- `warning/info` se reportan en `docs/todo.md`.
