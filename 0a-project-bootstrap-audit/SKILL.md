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
python ~/.config/agents/skills/0a-project-bootstrap-audit/scripts/bootstrap_gate.py --repo-root . --check
```

## Resultado

- Audita estado minimo de bootstrap (estructura base/layout) sin modificar codigo.
- Solo genera/actualiza/modifica `docs/todo.md`.

## Validaciones

- **Layout**: Directorios base, archivos esenciales, `.gitkeep` solo en dirs vacios
- **Env**: Existencia de `.env` y `.env.example`, paridad basica de keys
- **Python**: `__init__.py` en todos los directorios bajo `src/`
