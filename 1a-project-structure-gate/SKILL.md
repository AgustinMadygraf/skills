---
name: 1a-project-structure-gate
description: "Auditoria de estructura mecánica: env/layout/python-file. SIN layer-boundary ni SOLID."
---

# Project Structure Audit

Skill de auditoria de estructura y convenciones mecánicas de archivos Python.  
**Scope limitado**: NO incluye validación de arquitectura (layer-boundary) ni principios SOLID.

## Activación

- Uso explícito únicamente: `$1a-project-structure-gate`.

## Comando

```bash
python ~/.config/agents/skills/1a-project-structure-gate/scripts/structure_gate.py --repo-root .
```

> **Nota**: Este comando ejecuta solo el `structure-gate` (env/layout/python-file).  
> Para layer-boundary usar `2a-layer-boundary-gate`.  
> Para SOLID usar `3a-solid-gate`.

## Política: Solo Auditoría, Sin Corrección

**1a es puramente auditiva**: detecta problemas y reporta, pero **nunca modifica código**.  
Para correcciones automáticas usar `1b-project-structure-repair`.

| Modo | Comportamiento |
|------|----------------|
| `PASS` (verde) | Estructura correcta. `docs/todo.md` se actualiza (sin tareas pendientes). |
| `WARN` (amarillo) | Issues no críticos detectados. Se registran en `docs/todo.md`. |
| `FAIL` (rojo) | Violaciones críticas detectadas. Se registran en `docs/todo.md`.

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

### Exports y Re-exports (R1.1 y R1.3)

Valida consistencia de `__all__` en archivos de API pública:

| Regla | Descripción | Ejemplo válido |
|-------|-------------|----------------|
| `export_not_found` | Nombre en `__all__` no existe en el archivo | Importar desde submódulo: `from .x import y` |
| `empty_export` | `__all__ = []` sin elementos | Debe tener al menos un export o eliminarse |
| `broken_reexport` | Nombre en `__all__` no está importado ni definido | `from .sub import x` → `__all__ = ["x"]` |

```python
# ✅ CORRECTO: Re-export desde submódulo
from src.use_cases.quote_pdf.renderer import get_quote_pdf_bytes
__all__ = ["get_quote_pdf_bytes"]

# ❌ VIOLACIÓN: En __all__ pero no existe
__all__ = ["get_quote_pdf"]  # Error: no importado ni definido
```

## Resultado

| Estado | Código | Descripción |
|--------|--------|-------------|
| ✅ `PASS` | 0 | Todas las políticas de estructura pasan. |
| ⚠️ `WARN` | 0 | Issues menores detectados (documentados en `docs/todo.md`). |
| ❌ `FAIL` | != 0 | Violaciones críticas detectadas (documentadas en `docs/todo.md`). |

**Formato en `docs/todo.md`**:
- `[layout-policy]` - Estructura de directorios
- `[env-policy]` - Variables de entorno  
- `[python-file-policy]` - Convenciones de archivos Python (`__init__.py`, docstrings, imports, exports, dataclasses)

> **Nota**: Esta skill NO genera entradas `[layer-boundary:*]` ni `[solid-*:*]`. Usar skills `2a` y `3a` respectivamente.
> **Esta skill NO modifica código fuente**. Solo audita y documenta.

## Límites de Responsabilidad

Esta skill se enfoca exclusivamente en **estructura y convenciones mecánicas**. NO incluye:

| Área | Skill correcta |
|------|----------------|
| Fronteras entre capas (dependencias) | `2a-layer-boundary-gate` |
| Principios SOLID (SRP, DIP, ISP) | `3a-solid-gate` |

## Notas de Diseño

### Enfoque Predictivo vs Reactivo
1a es **proactivo/predictivo**: detecta TODAS las violaciones de estructura, no solo las que están en `docs/todo.md`. Esto permite:

- Descubrir problemas ocultos (como exports rotos que pasan desapercibidos)
- Tener una visión completa del estado del proyecto
- Priorizar reparaciones antes de ejecutar 1b

### Relación con 1b
1a detecta → documenta en `docs/todo.md` → 1b lee y repara lo mecánico

Las violaciones de dataclasses en capas incorrectas requieren decisión humana (no son mecánicas).
