---
name: 0b-project-bootstrap-repair
description: "Repair de bootstrap: crea/normaliza estructura y archivos base del proyecto."
---

# Project Bootstrap Repair

Skill de reparacion para bootstrap y estructura base.

## Activacion

- Uso explicito unicamente: `$0b-project-bootstrap-repair`.

## Comando

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --structure-gate-only --fix-python
```

## Resultado

- Repara faltantes de estructura base.
- Normaliza python-file policy mecanica (Path/import order/__init__) cuando aplique.
- Si quedan violaciones, las deja reflejadas en `docs/todo.md`.
