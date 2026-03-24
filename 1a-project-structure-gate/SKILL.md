---
name: 1a-project-structure-gate
description: "Auditoria de estructura: env/layout/python-file; registra salida en docs/todo.md."
---

# Project Structure Audit

Skill de auditoria de estructura y convenciones mecánicas.

## Activación

- Uso explícito únicamente: `$1a-project-structure-gate`.

## Comando

```bash
python ~/.config/agents/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --check
```

## Validaciones de Estructura

### Layout Policy
- Exige que `.gitignore` contenga la entrada exacta `.tmp/`.
- Exige `.gitkeep` solo en directorios base **vacíos** (sin archivos ni subdirectorios con contenido).
- Exige directorios base pre-establecidos.

### Python File Policy

#### `__init__.py`
- Exige `__init__.py` vacíos en directorios pre-establecidos (`src/` y subdirectorios de capas).
- **Preserva `__init__.py` con `__all__` o imports de re-export (API pública).**

#### Docstrings
- Exige docstrings de Path al inicio de cada archivo.

#### Imports
- Exige orden de imports según política de capas (infrastructure → interface_adapters → use_cases → entities).
- **Elimina imports no usados** (dead code detection).

#### Dataclasses (R2)
Política granular siguiendo Clean Architecture:
- ✅ `entities/`: Permitido (Value Objects, entidades)
- ✅ `infrastructure/`: Permitido (configuración, settings)
- ❌ `use_cases/`: Prohibido (siempre comportamiento)
- ⚡ `interface_adapters/`: **Condicional**
  - ✅ **Permitido** si es DTO (sufijos permitidos, singular o plural):
    - `_model.py` / `_models.py`
    - `_dto.py` / `_dtos.py`
    - `_request.py` / `_requests.py`
    - `_response.py` / `_responses.py`
    - `_view_model.py` / `_view_models.py`
    - `_vm.py` / `_vms.py`
  - ❌ **Prohibido** si es adaptador con comportamiento

### Exports y Re-exports (Nuevo R1.1 y R1.3)

#### R1.1: Exports Consistentes
Valida que todos los nombres en `__all__` estén **definidos o importados** en el archivo:

```python
# ❌ VIOLACIÓN: __all__ declara 'ChatwootGateway' pero no existe
__all__ = ["ChatwootGateway"]  # No importado, no definido

# ✅ CORRECTO: Importado para re-export
from src.use_cases.ports.chatwoot_gateway import ChatwootGateway
__all__ = ["ChatwootGateway"]
```

Violación reportada: `inconsistent_export:__all__ declares 'X' but not defined or imported`

#### R1.3: Re-export Pattern
Valida patrones de re-export correctos:

```python
# ❌ VIOLACIÓN: __all__ vacío
__all__ = []

# ❌ VIOLACIÓN: 'X' en __all__ pero no importado desde submódulo
__all__ = ["get_quote_pdf"]  # No está importado de quote_pdf/renderer

# ✅ CORRECTO: Re-export desde submódulo
from src.use_cases.quote_pdf.renderer import get_quote_pdf_bytes
__all__ = ["get_quote_pdf_bytes"]
```

Violaciones reportadas:
- `empty_export:__all__ is empty`
- `broken_reexport:'X' in __all__ but not imported from submodule`

## Resultado

- Falla con código != 0 si no pasa env/layout/python-file policy.
- Actualiza `docs/todo.md` con violaciones detectadas en formato:
  - `[layout-policy]` - Estructura de directorios
  - `[env-policy]` - Variables de entorno
  - `[python-file-policy]` - Convenciones de archivos Python
  - `[layer-boundary:*]` - Fronteras de capas (para skills 2a/2b)
  - `[solid-*:*]` - Principios SOLID (para skills 3a/3b)

## Notas de Diseño

### Enfoque Predictivo vs Reactivo
1a es **proactivo/predictivo**: detecta TODAS las violaciones posibles, no solo las que están en `docs/todo.md`. Esto permite:

- Descubrir problemas ocultos (como exports rotos que pasan desapercibidos)
- Tener una visión completa del estado del proyecto
- Priorizar reparaciones antes de ejecutar 1b

### Relación con 1b
1a detecta → documenta en `docs/todo.md` → 1b lee y repara lo mecánico

Las violaciones de dataclasses y arquitectura requieren decisión humana (no son mecánicas).
