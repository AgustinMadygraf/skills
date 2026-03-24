---
name: 2b-layer-boundary-repair
description: "Repair de fronteras entre capas: aplica fixes mecanicos de bajo riesgo para violaciones de layer-boundary."
---

# Layer Boundary Repair

Skill de reparacion acotada para hallazgos de fronteras entre capas.

## Activacion

- Uso explicito: `$2b-layer-boundary-repair`.

## Comando

```bash
# Recomendado: primero dry-run
python ~/.codex/skills/2b-layer-boundary-repair/scripts/layer_boundary_repair.py --repo-root .

# Aplicar cambios mecanicos
python ~/.codex/skills/2b-layer-boundary-repair/scripts/layer_boundary_repair.py --repo-root . --apply
```

## Resultado

- Aplica solo reparaciones mecanicas y deterministas (bajo riesgo).
- Ejemplos de fixes:
  - crea directorios faltantes de capas
  - crea `__init__.py` faltantes en capas
- Re-audita y actualiza `docs/todo.md` con el estado posterior.
- Hallazgos ambiguos o no deterministas quedan en `docs/todo.md`.
