# Audit Utils

Utilidades compartidas para skills de auditoría (0a, 1a, 2a, 3a).

## Uso

```python
import sys
from pathlib import Path

# Agregar shared/ al path
SKILL_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT / "shared"))

from audit_utils import (
    Finding,
    ReportBuilder,
    TodoWriter,
    parse_ast,
    py_files,
    relative_to_repo,
)
```

## Módulos

### `files.py`

Utilidades de filesystem:

- `py_files(root, exclude_init=True)` - Lista archivos .py
- `src_dirs(repo_root)` - Lista directorios bajo src/
- `parse_ast(path)` - Parsea archivo a AST
- `relative_to_repo(path, repo_root)` - Ruta relativa con forward slashes

### `report.py`

Estructuras de reporte:

- `Finding` - Dataclass para un hallazgo (severity, rule, file, line, detail)
- `Report` - Reporte completo con conteos por severidad
- `ReportBuilder` - Builder para construir reportes

```python
builder = ReportBuilder()
builder.add_critical("rule_name", "file.py", 10, "descripcion")
builder.add_warning("other_rule", "file.py", 20, "otro detalle")
report = builder.build()

print(report.ok)  # False (tiene críticos)
print(report.to_dict())  # Dict serializable
```

### `todo_writer.py`

Gestión de `docs/todo.md`:

```python
writer = TodoWriter(repo_root, "skill-name")
writer.write_findings(findings, title="Skill Title")
```

## Versión

`1.0.0`

## Notas

- Solo utilidades puras sin estado
- NO incluye lógica de reglas específicas
- Cada skill mantiene sus propias reglas de negocio
