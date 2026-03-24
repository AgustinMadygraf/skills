---
name: 3a-solid-gate
description: "Gate SOLID-lite: valida SRP, DIP, ISP con severidades. Perfiles lite y strict."
---

# SOLID Gate

Valida principios SOLID-lite en el codigo: SRP, DIP, ISP.

## Activacion

- Uso explicito: `$3a-solid-gate`.

## Comando

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check
```

Modo audit puro:

- Solo genera/actualiza/modifica `docs/todo.md`.
- No escribe reportes ni otros archivos auxiliares por defecto.

## Perfil SOLID (gradual)

- `lite` (default, obligatorio)
- `strict` (opt-in)

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --solid-profile strict
```

## Prevencion de regresiones

1. Crear baseline inicial:

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --write-solid-baseline
```

2. Enforzar baseline en corridas futuras:

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --enforce-solid-baseline
```

## Exemptions registry (trazable y temporal)

Archivo de registro (opcional):

- `docs/architecture/solid-exemptions.json`

Override de ruta:

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --solid-exemptions docs/architecture/solid-exemptions.json
```

Alerta de vencimiento proximo:

```bash
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --exemptions-expiry-warning-days 7
```

Formato recomendado:

```json
{
  "exemptions": [
    {
      "id": "EX-001",
      "enabled": true,
      "rule": "srp_large_class",
      "file": "src/use_cases/*.py",
      "line": 6,
      "reason": "Refactor planificado para proximo sprint",
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
python ~/.codex/skills/3a-solid-gate/scripts/solid_gate.py --repo-root . --check --solid-thresholds docs/architecture/solid-thresholds.json
```

## Gate

- Falla con codigo != 0 si existen hallazgos `critical`.
- Incluye `solid-lite`:
  - SRP-lite (modulos/clases demasiado cargados)
  - DIP-lite (imports de vendors en capas internas y uso sospechoso de concretos)
  - ISP-lite (interfaces gateway demasiado grandes)
- Si `--solid-profile strict`:
  - agrega reglas strict (SRP/ISP/DIP mas exigentes + OCP por cadenas condicionales largas)
  - puede fallar por hallazgos `critical` de `solid-strict`
- Falla con codigo != 0 si hay hallazgos nuevos respecto del baseline (cuando `--enforce-solid-baseline` esta activo).
- `warning/info` se reportan en `docs/todo.md`.
