---
name: 3b-solid-refactor-assistant
description: "Asistente de refactor SOLID guiado para resolver hallazgos SRP/DIP/ISP sin autofix ciego."
---

# SOLID Refactor Assistant

Skill para ejecutar refactors SOLID de manera explicita y segura.

## Activacion

- Uso explicito: `$3b-solid-refactor-assistant`.

## Objetivo

- Tomar hallazgos de `docs/todo.md` (especialmente `solid-*`).
- Proponer refactor por lotes pequenos con impacto acotado.
- Aplicar cambios solo con trazabilidad y validacion posterior.

## Comando recomendado

```bash
python ~/.codex/skills/3b-solid-refactor-assistant/scripts/generate_solid_refactor_plan.py --repo-root .
```

Salida principal:

- `docs/refactor/solid-refactor-plan.md`

## Sugerencias de patch (sin aplicar)

```bash
python ~/.codex/skills/3b-solid-refactor-assistant/scripts/generate_solid_patch_suggestions.py --repo-root .
```

Salida principal:

- `docs/refactor/solid-patch-suggestions.md`

## Analizar clase especifica

```bash
python ~/.codex/skills/3b-solid-refactor-assistant/scripts/analyze_class_solid.py --repo-root . --file src/use_cases/example.py --class ExampleUseCase
```

Salida:

- Analisis SRP, DIP, ISP de la clase
- Recomendaciones especificas
- Metricas de complejidad

## Reglas

- No hacer autofix masivo ciego.
- No cambiar comportamiento funcional sin justificar.
- Priorizar extraer responsabilidades y reducir acoplamiento.
- Luego del refactor, re-ejecutar:
  - `$3a-solid-gate`
