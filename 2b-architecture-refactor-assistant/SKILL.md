---
name: 2b-architecture-refactor-assistant
description: "[DEPRECATED] Asistente de refactor arquitectonico. Usar 3b-solid-refactor-assistant."
maturity: deprecated
---

# ⚠️ DEPRECATED - Architecture Refactor Assistant

**Esta skill esta deprecada.** Se reemplazo por:

- **Fase 3**: [`3b-solid-refactor-assistant`](../3b-solid-refactor-assistant/SKILL.md) - Asistente de refactor SOLID

## Motivo de deprecacion

La skill original estaba acoplada a la skill 2a deprecada. El nuevo flujo de refactor SOLID esta en la fase 3.

## Migracion

```bash
# Antes (deprecated)
python ~/.codex/skills/2b-architecture-refactor-assistant/scripts/generate_refactor_plan.py --repo-root .

# Ahora (nuevo)
python ~/.codex/skills/3b-solid-refactor-assistant/scripts/generate_solid_refactor_plan.py --repo-root .
```
