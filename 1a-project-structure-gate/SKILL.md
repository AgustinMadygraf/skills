---
name: 1a-project-structure-gate
description: "Auditoria de estructura: env/layout/python-file; registra salida en docs/todo.md."
---

# Project Structure Audit

Skill de auditoria de estructura y convenciones mecanicas.

## Activacion

- Uso explicito unicamente: `$1a-project-structure-gate`.

## Comando

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --structure-gate-only --check
```

## Resultado

- Falla con codigo != 0 si no pasa env/layout/python-file policy.
- Exige que `.gitignore` contenga la entrada exacta `.tmp/`.
- Solo genera/actualiza/modifica `docs/todo.md`.
