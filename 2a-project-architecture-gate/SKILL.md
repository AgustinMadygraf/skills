---
name: 2a-project-architecture-gate
description: "[DEPRECATED] Gate estricto de arquitectura. Usar 2a-layer-boundary-gate + 3a-solid-gate."
maturity: deprecated
---

# ⚠️ DEPRECATED - Project Architecture Gate

**Esta skill esta deprecada.** Se dividio en dos skills especializadas:

- **Fase 2**: [`2a-layer-boundary-gate`](../2a-layer-boundary-gate/SKILL.md) - Valida fronteras entre capas
- **Fase 3**: [`3a-solid-gate`](../3a-solid-gate/SKILL.md) - Valida principios SOLID

## Motivo de deprecacion

La skill original combinaba dos responsabilidades distintas:
1. Validacion de fronteras entre capas (layer-boundary)
2. Validacion de principios SOLID

Siguiendo el principio SRP, se dividio en dos skills mas enfocadas.

## Migracion

```bash
# Antes (deprecated)
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check

# Ahora (nuevo)
python ~/.codex/skills/2a-layer-boundary-gate/scripts/layer_boundary_gate.py --repo-root . --check
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check
```
