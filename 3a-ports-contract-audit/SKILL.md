---
name: 3a-ports-contract-audit
description: "Auditoria de contratos/puertos: naming, ubicacion y dependencias desde use_cases, con salida en docs/todo.md."
---

# Ports Contract Audit

Skill de auditoria enfocada en puertos y contratos de arquitectura.

## Activacion

- Uso explicito unicamente: `$3a-ports-contract-audit`.

## Comando

```bash
python ~/.codex/skills/3a-ports-contract-audit/scripts/ports_contract_audit.py --repo-root .
```

## Resultado

- Solo genera/actualiza/modifica `docs/todo.md`.
- Verifica:
  - contratos en `src/interface_adapters/gateways/`
  - imports de `use_cases` hacia puertos (no concretos)
  - consistencia minima de naming de puertos.
