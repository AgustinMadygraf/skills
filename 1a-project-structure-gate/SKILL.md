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
python ~/.config/agents/skills/1a-project-structure-gate/scripts/structure_gate.py --repo-root . --check
```

## Resultado

- Falla con codigo != 0 si no pasa env/layout/python-file policy.
- Exige que `.gitignore` contenga la entrada exacta `.tmp/`.
- Exige `.gitkeep` solo en directorios base **vacíos** (sin archivos ni subdirectorios con contenido).
- Exige `__init__.py` vacios solo en directorios pre-establecidos (`src/` y subdirectorios de capas).
- **Preserva `__init__.py` con `__all__` o imports de re-export (API pública).**
- Exige docstrings de Path al inicio de cada archivo.
- Exige orden de imports segun politica de capas.
- **Prohíbe dataclasses en `use_cases/` e `interface_adapters/` (lógica de negocio), permite en `entities/` (DTOs) e `infrastructure/` (config).**
- Actualiza `docs/todo.md` con violaciones detectadas.
