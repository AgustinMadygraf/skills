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
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --structure-gate-only --fix-python
```

## Resultado

- Repara faltantes mecanicos de estructura y python-file policy.
- Si falta `.tmp/` en `.gitignore`, lo agrega automaticamente.
- Actualiza `docs/todo.md` con estado posterior.
