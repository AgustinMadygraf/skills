---
name: 3b-ports-contract-repair
description: "Repair de contratos/puertos: aplica fixes mecanicos de bajo riesgo y actualiza docs/todo.md."
---

# Ports Contract Repair

Skill de reparacion acotada para hallazgos de contratos y puertos.

## Activacion

- Uso explicito unicamente: `$3b-ports-contract-repair`.

## Comando

```bash
# Recomendado: primero dry-run
python ~/.codex/skills/3b-ports-contract-repair/scripts/ports_contract_repair.py --repo-root .

# Aplicar cambios mecanicos
python ~/.codex/skills/3b-ports-contract-repair/scripts/ports_contract_repair.py --repo-root . --apply
```

## Resultado

- Aplica solo reparaciones mecanicas y deterministas (bajo riesgo).
- Ejemplos de fixes:
  - crea `src/interface_adapters/gateways/` si falta
  - crea `src/interface_adapters/gateways/__init__.py` si falta
- Re-audita y actualiza `docs/todo.md` con el estado posterior.
- Hallazgos ambiguos o no deterministas quedan en `docs/todo.md`.
