# Skills Operations

Ecosistema de skills para auditoria y reparacion de proyectos Python con Clean Architecture.

## Nuevo esquema de skills (v2)

| Fase                  | Audit (gate)                  | Repair (fix)                  |
|-----------------------|-------------------------------|-------------------------------|
| 0 - Bootstrap         | `0a-project-bootstrap-audit`  | `0b-project-bootstrap-repair` |
| 1 - Estructura        | `1a-project-structure-gate`   | `1b-project-structure-repair` |
| 2 - Layer Boundary    | `2a-layer-boundary-gate`      | `2b-layer-boundary-repair`    |
| 3 - SOLID             | `3a-solid-gate`               | `3b-solid-refactor-assistant` |
| 4 - Puertos           | `4a-ports-contract-audit`     | `4b-ports-contract-repair`    |

### Flujo de uso

```powershell
# Fase 0: Bootstrap (solo si el proyecto es nuevo)
$0a-project-bootstrap-audit
$0b-project-bootstrap-repair

# Fase 1: Estructura basica
$1a-project-structure-gate
$1b-project-structure-repair

# Fase 2: Fronteras entre capas
$2a-layer-boundary-gate
$2b-layer-boundary-repair

# Fase 3: Calidad SOLID
$3a-solid-gate
$3b-solid-refactor-assistant

# Fase 4: Contratos/Puertos
$4a-ports-contract-audit
$4b-ports-contract-repair
```

## Comandos de rutina

```powershell
# Validacion completa
python shared/scripts/preflight_skills.py

# Migrar skills legacy al baseline de gobernanza
python shared/scripts/migrate_legacy_skills.py

# Crear scaffold de un nuevo skill
python shared/scripts/bootstrap_new_skill.py my-new-skill --description "..."

# Sincronizar catalogo AGENTS.md
python shared/scripts/sync_agents_catalog.py

# Generar reporte de salud
python shared/scripts/skills_health_report.py

# Bump de version + changelog
python shared/scripts/bump_skill_version.py skill-backend-testing 1.2.0 --note "..."
```

## Migracion desde esquema anterior

Las siguientes skills estan **deprecated** y se reemplazan por las nuevas:

| Skill vieja | Reemplazo |
|-------------|-----------|
| `2a-project-architecture-gate` | `2a-layer-boundary-gate` + `3a-solid-gate` |
| `2b-architecture-refactor-assistant` | `3b-solid-refactor-assistant` |
| `3a-ports-contract-audit` | `4a-ports-contract-audit` |
| `3b-ports-contract-repair` | `4b-ports-contract-repair` |
