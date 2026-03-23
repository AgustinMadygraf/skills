---
name: 00-project-bootstrap
description: "Scaffold minimo de proyecto (estructura + archivos base) sin usarlo como gate de calidad."
---

# Project Bootstrap

Skill para crear el esqueleto inicial de proyecto.

## Activacion

- Uso explicito unicamente: `$00-project-bootstrap`.

## Flujo

1. Ejecutar:

```bash
python ~/.codex/skills/01-project-structure-gate/scripts/project_gate.py --repo-root . --scaffold-only
```

2. Si se desea completar contenido faltante aunque ya exista, agregar `--force`.
3. Si se desea normalizar encabezados/imports Python, agregar `--fix-python`.

## Resultado esperado

- Estructura base de carpetas y archivos iniciales creada.
- Evidencia en `.tmp/bootstrap.json`.
- `docs/todo.md` actualizado con pendientes automaticos detectados.

## Reglas

- No usar esta skill como gate final de calidad.
- Para auditoria estricta usar `$01-project-structure-gate` y luego `$02a-project-architecture-gate`.
