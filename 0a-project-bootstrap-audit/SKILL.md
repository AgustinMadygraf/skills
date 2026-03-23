---
name: 0a-project-bootstrap-audit
description: "Auditoria de bootstrap: valida estructura base y registra salida en docs/todo.md."
---

# Project Bootstrap Audit

Skill de auditoria de bootstrap inicial.

## Activacion

- Uso explicito unicamente: `$0a-project-bootstrap-audit`.

## Comando

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --bootstrap-gate-only --check
```

## Resultado

- Audita estado minimo de bootstrap (estructura base/layout) sin modificar codigo.
- Solo genera/actualiza/modifica `docs/todo.md`.
