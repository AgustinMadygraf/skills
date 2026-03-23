---
name: 1-project-structure-gate
description: "Gate estricto de estructura: env/layout/python-file; actualiza docs/todo.md."
---

# Project Structure Gate

Valida politicas mecanicas y de estructura del proyecto.

## Activacion

- Uso explicito unicamente: `$1-project-structure-gate`.

## Comando

```bash
python ~/.codex/skills/1-project-structure-gate/scripts/project_gate.py --repo-root . --structure-gate-only --check
```

## Gate

- Falla con codigo != 0 si no pasa env/layout/python-file policy.
- Exige que `.gitignore` contenga la entrada exacta `.tmp/`.
- Actualiza `docs/todo.md` con tareas de estructura.
