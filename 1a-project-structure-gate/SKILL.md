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
- **Política granular de dataclasses (Clean Architecture):**
  - ✅ `entities/`: Permitido (Value Objects, entidades)
  - ✅ `infrastructure/`: Permitido (configuración, settings)
  - ❌ `use_cases/`: Prohibido (siempre comportamiento)
  - ⚡ `interface_adapters/`: **Condicional**
    - ✅ **Permitido** si es DTO (sufijos permitidos, singular o plural):
      - `_model.py` / `_models.py` (ej: `request_model.py`, `request_models.py`)
      - `_dto.py` / `_dtos.py`
      - `_request.py` / `_requests.py`
      - `_response.py` / `_responses.py`
      - `_view_model.py` / `_view_models.py`
      - `_vm.py` / `_vms.py`
    - ❌ **Prohibido** si es adaptador con comportamiento (ej: `*_presenter.py`, `*_controller.py`)
  
  *Rationale: Los DTOs (Request/Response Models, ViewModels) son datos de serialización y SÍ pueden usar dataclasses. Se aceptan sufijos plurales siguiendo convención FastAPI (ej: `schemas.py`, `models.py`). Los adaptadores con comportamiento deben usar clases normales (SRP).*
- Actualiza `docs/todo.md` con violaciones detectadas.
- Actualiza `docs/todo.md` con violaciones detectadas.
