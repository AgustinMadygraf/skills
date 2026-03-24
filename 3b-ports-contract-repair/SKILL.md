---
name: 3b-ports-contract-repair
description: "[DEPRECATED] Repair de contratos/puertos. Usar 4b-ports-contract-repair."
maturity: deprecated
---

# ⚠️ DEPRECATED - Ports Contract Repair

**Esta skill esta deprecada.** Se movio a la fase 4:

- **Fase 4**: [`4b-ports-contract-repair`](../4b-ports-contract-repair/SKILL.md) - Repair de contratos/puertos

## Motivo de reenumeracion

La numeracion se ajusto para reflejar mejor el orden de aplicacion:
- Fase 2: Layer boundaries
- Fase 3: SOLID
- Fase 4: Ports/Contracts (depende de que las capas y SOLID esten correctos)

## Migracion

```bash
# Antes (deprecated)
python ~/.codex/skills/3b-ports-contract-repair/scripts/ports_contract_repair.py --repo-root .

# Ahora (nuevo)
python ~/.codex/skills/4b-ports-contract-repair/scripts/ports_contract_repair.py --repo-root .
```
