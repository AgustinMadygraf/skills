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
python ~/.config/agents/skills/0b-project-bootstrap-repair/scripts/bootstrap_repair.py --repo-root .
```

## Resultado

- Crea directorios base faltantes.
- Crea archivos esenciales faltantes (run.py, README.md, .env, .env.example, logger.py, config.py).
- Crea `__init__.py` faltantes en `src/`.
- Crea `.gitkeep` solo en directorios vacios que lo requieran.
- Agrega `.tmp/` a `.gitignore` si falta.
- Si quedan violaciones complejas, se registran en `docs/todo.md`.
