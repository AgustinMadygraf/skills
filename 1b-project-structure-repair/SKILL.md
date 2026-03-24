---
name: 1b-project-structure-repair
description: "Repair de estructura REACTIVO: lee docs/todo.md y ejecuta reparaciones basadas en hallazgos de 1a."
---

# Project Structure Repair (REACTIVO)

Skill de reparación **reactiva** para hallazgos de estructura. 

**IMPORTANTE**: Este skill NO detecta violaciones por sí mismo. Lee `docs/todo.md` 
generado por `$1a-project-structure-gate` y ejecuta las reparaciones necesarias.

## Flujo de trabajo

```
$1a-project-structure-gate  →  Detecta → Escribe docs/todo.md
         ↓
$1b-project-structure-repair  →  Lee docs/todo.md → Repara → Actualiza estado
```

## Activación

- Uso explícito: `$1b-project-structure-repair`.

## Comando

```bash
python ~/.codex/skills/1b-project-structure-repair/scripts/structure_repair.py --repo-root .
```

## Qué repara (basado en docs/todo.md)

| Tipo en todo.md | Acción |
|-----------------|--------|
| `[layout-policy]` / `[bootstrap-policy]` | Crea `.gitkeep` en directorios vacíos, crea directorios faltantes |
| `[env-policy]` | Sincroniza keys entre `.env` y `.env.example` |
| `[python-file-policy]` | Ordena imports, arregla docstrings, elimina imports no usados, vacía `__init__.py` sin exports |
| `[layer-boundary:*]` | **NO repara** → Usar skill `2b` |
| `[solid-*:*]` | **NO repara** → Usar skill `3b` |

## Qué NO hace

- **NO detecta violaciones**: Eso es responsabilidad de `$1a-project-structure-gate`
- **NO repara violaciones de arquitectura**: Layer boundaries, SOLID → Skills 2b/3b
- **NO crea archivos esenciales complejos**: `README.md`, `run.py`, configuraciones → Manual o skill `0b`

## Resultado

- Ejecuta reparaciones mecánicas basadas **estrictamente** en `docs/todo.md`
- Archiva tareas completadas `[x]` de `docs/todo.md` hacia `docs/todo.done.md`
- Reporta acciones realizadas por categoría
- Sugiere re-ejecutar `$1a-project-structure-gate` para verificar

## Ejemplo de uso

```bash
# 1. Detectar violaciones
$1a-project-structure-gate

# 2. Reparar basado en lo detectado  
$1b-project-structure-repair

# 3. Verificar estado
$1a-project-structure-gate
```

## Notas de diseño

**Enfoque reactivo vs proactivo**:

- **Antes (proactivo)**: 1b re-detectaba violaciones con su propia lógica
- **Ahora (reactivo)**: 1b solo repara lo que 1a documentó en `docs/todo.md`

**Beneficios**:
- Sin duplicación de lógica entre 1a y 1b
- Traza clara: auditoría → documentación → reparación
- Si 1a tiene un falso positivo, 1b no lo "arregla" sorpresivamente
- Cada skill tiene una responsabilidad única (SRP)
