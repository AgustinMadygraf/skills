---
name: 2a-project-architecture-gate
description: "Gate estricto de arquitectura: layer-boundary/import-boundary + solid-lite (SRP/DIP/ISP) con severidades."
---

# Project Architecture Gate

Valida fronteras de arquitectura limpia por capas y un set SOLID-lite.

## Activacion

- Uso explicito unicamente: `$2a-project-architecture-gate`.

## Comando

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check
```

Modo audit puro:

- Solo genera/actualiza/modifica `docs/todo.md`.
- No escribe reportes ni otros archivos auxiliares por defecto.

Perfil SOLID (gradual):

- `lite` (default, obligatorio)
- `strict` (opt-in)

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --solid-profile strict
```

## Prevencion de regresiones

1. Crear baseline inicial:

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --write-architecture-baseline
```

2. Enforzar baseline en corridas futuras:

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --enforce-architecture-baseline
```

## Exemptions registry (trazable y temporal)

Archivo de registro (opcional):

- `docs/architecture/exemptions.json`

Override de ruta:

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --architecture-exemptions docs/architecture/exemptions.json
```

Alerta de vencimiento proximo:

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --exemptions-expiry-warning-days 7
```

Formato recomendado:

```json
{
  "exemptions": [
    {
      "id": "EX-001",
      "enabled": true,
      "rule": "use_cases_imports_infrastructure",
      "file": "src/use_cases/*.py",
      "line": 6,
      "reason": "Migracion incremental a puertos",
      "owner": "arquitectura",
      "expires_on": "2026-06-30"
    }
  ]
}
```

Reglas:

- `expires_on` es obligatorio (ISO date) y vencido invalida la excepcion.
- `owner` y `reason` son obligatorios.
- `file` permite patron tipo glob (`*`).
- Si una excepcion vence en `N` dias o menos (default `7`), se registra warning `exemption_expiring_soon`.

## Calibracion solid-lite

Archivo de configuracion (opcional):

- `docs/architecture/solid-thresholds.json`

Claves soportadas:

- `max_use_case_classes_per_module`
- `max_use_case_top_level_functions`
- `max_gateway_public_methods`
- `max_public_methods_per_class`
- `max_use_case_top_level_functions_strict`
- `max_gateway_public_methods_strict`
- `max_public_methods_per_class_strict`
- `max_ocp_conditional_branches_strict`

Override de ruta:

```bash
python ~/.codex/skills/1a-project-structure-gate/scripts/project_gate.py --repo-root . --architecture-gate-only --check --solid-thresholds docs/architecture/solid-thresholds.json
```

## Gate

- Falla con codigo != 0 si existen hallazgos `critical`.
- `presenters_imports_controllers` se considera `critical`.
- Incluye `solid-lite`:
  - SRP-lite (modulos/clases demasiado cargados)
  - DIP-lite (imports de vendors en capas internas y uso sospechoso de concretos)
  - ISP-lite (interfaces gateway demasiado grandes)
- Si `--solid-profile strict`:
  - agrega reglas strict (SRP/ISP/DIP mas exigentes + OCP por cadenas condicionales largas)
  - puede fallar por hallazgos `critical` de `solid-strict`
- Falla con codigo != 0 si hay hallazgos nuevos respecto del baseline (cuando `--enforce-architecture-baseline` esta activo).
- `warning/info` se reportan en `docs/todo.md`.
