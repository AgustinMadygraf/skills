# Skills Operations

Comandos de rutina para operar el ecosistema de skills:

```powershell
# Validacion completa
python skills/shared/scripts/preflight_skills.py

# Migrar skills legacy al baseline de gobernanza
python skills/shared/scripts/migrate_legacy_skills.py

# Crear scaffold de un nuevo skill
python skills/shared/scripts/bootstrap_new_skill.py my-new-skill --description "..."

# Sincronizar catalogo AGENTS.md
python skills/shared/scripts/sync_agents_catalog.py

# Generar reporte de salud
python skills/shared/scripts/skills_health_report.py

# Bump de version + changelog
python skills/shared/scripts/bump_skill_version.py skill-backend-testing 1.2.0 --note "..."
```
