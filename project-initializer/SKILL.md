---
name: project-initializer
description: "Inicializa un proyecto base con interrogatorio minimo, estructura de carpetas de arquitectura limpia, archivos semilla y validacion de paridad entre .env y .env.example."
---

# Project Initializer

Skill de bootstrap inicial para arrancar un proyecto desde cero.

## Activacion

- Uso explicito unicamente: `\$project-initializer`.

## Alcance

- Ejecutar un interrogatorio minimo de contexto de proyecto.
- Persistir respuestas solo en `README.md`.
- Crear estructura base de carpetas:
  - `src/entities/`
  - `src/use_cases/`
  - `src/interface_adapters/presenters/`
  - `src/interface_adapters/gateways/`
  - `src/infrastructure/`
  - `src/infrastructure/settings/`
  - `docs/`
  - `tests/`
- Crear `.gitkeep` en carpetas vacias, excepto `src/infrastructure/`.
- Crear archivos base:
  - `run.py` (vacio)
  - `README.md`
  - `.gitignore`
  - `.env`
  - `.env.example`
  - `src/infrastructure/settings/logger.py`
  - `src/infrastructure/settings/config.py`
- Validar paridad de claves entre `.env` y `.env.example`.

## Flujo obligatorio

1. Ejecutar `scripts/bootstrap_project.py`.
2. Si faltan respuestas del interrogatorio, pedirlas.
3. Construir estructura y archivos minimos.
4. Verificar paridad `.env`/`.env.example`.
5. Emitir resumen final con rutas creadas y validacion.

## Reglas

- No crear `.gitkeep` dentro de `src/infrastructure/`.
- Incluir `Path:` en encabezados de plantilla donde aplique.
- No sobreescribir archivos existentes salvo solicitud explicita (`--force`).

## Comando sugerido

```bash
python ~/.codex/skills/project-initializer/scripts/bootstrap_project.py --repo-root .
```

