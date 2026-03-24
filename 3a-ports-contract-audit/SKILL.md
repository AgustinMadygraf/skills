---
name: 3a-ports-contract-audit
description: "[DEPRECATED] Auditoria de contratos/puertos. Usar 4a-ports-contract-audit."
maturity: deprecated
---

# ⚠️ DEPRECATED - Ports Contract Audit

**Esta skill esta deprecada.** Se movio a la fase 4:

- **Fase 4**: [`4a-ports-contract-audit`](../4a-ports-contract-audit/SKILL.md) - Auditoria de contratos/puertos

## Motivo de reenumeracion

La numeracion se ajusto para reflejar mejor el orden de aplicacion:
- Fase 2: Layer boundaries
- Fase 3: SOLID
- Fase 4: Ports/Contracts (depende de que las capas y SOLID esten correctos)

## Migracion

```bash
# Antes (deprecated)
python ~/.codex/skills/3a-ports-contract-audit/scripts/ports_contract_audit.py --repo-root .

# Ahora (nuevo)
python ~/.codex/skills/4a-ports-contract-audit/scripts/ports_contract_audit.py --repo-root .
```
