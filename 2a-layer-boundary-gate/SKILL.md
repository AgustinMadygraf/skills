---
name: 2a-layer-boundary-gate
description: "Gate de fronteras entre capas: valida dependencias entre entities, use_cases, adapters e infrastructure."
---

# Layer Boundary Gate

Valida que las fronteras entre capas de Clean Architecture se respeten.

## Activacion

- Uso explicito: `$2a-layer-boundary-gate`.

## Comando

```bash
python ~/.codex/skills/2a-layer-boundary-gate/scripts/layer_boundary_gate.py --repo-root . --check
```

## Resultado

- Solo genera/actualiza/modifica `docs/todo.md`.
- No escribe reportes ni otros archivos auxiliares por defecto.

## Reglas de layer-boundary

| Direccion | Estado |
|-----------|--------|
| entities ← use_cases | ✅ Permitido |
| use_cases ← gateways | ✅ Permitido |
| use_cases ← infrastructure | ❌ Prohibido (critical) |
| gateways ← infrastructure | ✅ Permitido |
| presenters ← controllers | ❌ Prohibido (critical) |
| infrastructure ← * | ❌ Prohibido (critical) |

## Gate

- Falla con codigo != 0 si existen hallazgos `critical`.
- `presenters_imports_controllers` se considera `critical`.
- `use_cases_imports_infrastructure` se considera `critical`.
- `warning/info` se reportan en `docs/todo.md`.
