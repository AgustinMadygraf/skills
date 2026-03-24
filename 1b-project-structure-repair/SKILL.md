---
name: 1b-project-structure-repair
description: "Repair de estructura: corrige env/layout/python-file policy y actualiza docs/todo.md."
---

# Project Structure Repair

Skill de reparacion para hallazgos de estructura.

## Activacion

- Uso explicito unicamente: `$1b-project-structure-repair`.

## Comando

```bash
python ~/.config/agents/skills/1b-project-structure-repair/scripts/structure_repair.py --repo-root .
```

## Resultado

- Crea `.gitkeep` faltantes en directorios base **vacíos** (sin archivos ni subdirectorios con contenido).
- Crea `__init__.py` faltantes y vacia los existentes (excepto los con exports).
- Agrega/actualiza docstrings de Path en archivos .py.
- Ordena imports según política de capas (algoritmo seguro: preserva imports multilinea).
- Si falta `.tmp/` en `.gitignore`, lo agrega.
- **Archiva tareas completadas `[x]` de `docs/todo.md` hacia `docs/todo.done.md`.**
- Actualiza `docs/todo.md` con estado posterior.

## Limitaciones conocidas

- El auto-fix de import order está **desactivado** porque el algoritmo actual
  rompe imports multilinea (ej: `from x import (a, b)`). Las violaciones de
  import order deben corregirse manualmente.
