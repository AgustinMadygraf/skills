---
name: clean-architecture-orchestrator
description: "Orquestador de auditoria de Arquitectura Limpia en src/. Clasifica hallazgos en certezas y dudas, registra certezas en docs/todo.md, registra dudas en docs/decision/questions.md, luego ejecuta decision-helper y finalmente todo-workflow. Usar cuando se requiera evaluar cumplimiento de capas, dependencias y limites arquitectonicos con cierre operativo automatizado."
---

# Clean Architecture Orchestrator

Ejecutar una auditoria enfocada exclusivamente en Arquitectura Limpia y cerrar el flujo con decisiones y ejecucion.

## Alcance

- Auditar `src/`.
- Evaluar capas, limites, direccion de dependencias, puertos/adaptadores y acoplamiento arquitectonico.
- Excluir seguridad general, performance y testing que no sean necesarios para decidir arquitectura.

## Criterios de clasificacion

Clasificar cada hallazgo como:

- `certeza`: existe evidencia tecnica suficiente para proponer accion sin decision de alto nivel.
- `duda`: requiere decision arquitectonica (trade-off, impacto transversal o cambio de regla de capas).

## Matriz rigida de decision (obligatoria)

Para cada hallazgo calcular:

- `EVIDENCIA` (0-3):
  - 0: intuicion sin prueba.
  - 1: indicio parcial.
  - 2: evidencia clara en 1-2 archivos.
  - 3: evidencia fuerte y repetible en multiples puntos.
- `ALCANCE` (0-3):
  - 0: local.
  - 1: afecta modulo.
  - 2: afecta capa.
  - 3: afecta multiples capas/contextos.
- `RIESGO_DECISION` (0-3):
  - 0: cambio mecanico.
  - 1: bajo impacto de decision.
  - 2: trade-off relevante.
  - 3: alto riesgo de elegir mal.
- `REVERSIBILIDAD` (0-2):
  - 0: reversible en horas.
  - 1: reversible con costo moderado.
  - 2: dificil/costoso de revertir.

Score:

`SCORE_DUDA = RIESGO_DECISION + REVERSIBILIDAD + max(0, ALCANCE - EVIDENCIA)`

Regla de corte:

- Si `EVIDENCIA >= 2` y `SCORE_DUDA <= 2` => `certeza`.
- Si `SCORE_DUDA >= 3` => `duda`.
- Si empata en borde (`SCORE_DUDA == 2` y `ALCANCE >= 2`) => `duda`.

No usar criterio libre cuando exista informacion para puntuar.

### Helper de puntaje (usar siempre que sea posible)

Calcular puntaje con:

```bash
python ~/.codex/skills/clean-architecture-orchestrator/scripts/score_hallazgos.py --evidencia 2 --alcance 2 --riesgo-decision 1 --reversibilidad 1
```

Salida esperada:
- `SCORE_DUDA=<n>`
- `CLASIFICACION=certeza|duda`
- `PUNTAJE=EVIDENCIA=...`
- Línea markdown reutilizable para pegar en `docs/todo.md` o `docs/decision/questions.md`.

## Flujo obligatorio

1. Auditar Arquitectura Limpia en `src/`.
2. Escribir certezas en `docs/todo.md`.
3. Escribir dudas en `docs/decision/questions.md`.
4. Ejecutar `skill:decision-helper`.
5. Ejecutar `skill:todo-workflow`.

No alterar este orden.

## Gate de calidad antes de delegar

Antes de ejecutar `decision-helper` y `todo-workflow`, verificar:

1. Toda certeza tiene archivo y accion concreta.
2. Toda duda tiene al menos 2 opciones.
3. No hay item duplicado entre `docs/todo.md` y `docs/decision/questions.md`.
4. El conteo final de items coincide con el resumen reportado.

## Reglas de escritura

### `docs/todo.md` (certezas)

Registrar tareas accionables con formato breve:

```markdown
- [ ] [ARQ] Titulo de mejora
  - Archivo: `src/...`
  - Evidencia: violacion concreta
  - Puntaje: `EVIDENCIA=x ALCANCE=y RIESGO_DECISION=z REVERSIBILIDAD=w SCORE_DUDA=n`
  - Accion sugerida: cambio puntual
```

Prohibido escribir certezas sin puntaje.

### `docs/decision/questions.md` (dudas)

Registrar cada duda con estructura minima:

```markdown
### [YYYY-MM-DD] Pregunta arquitectonica
- Contexto: descripcion breve
- Evidencia: archivo(s) y regla violada
- Duda: decision a tomar
- Opciones: A | B | C
- Impacto: alto|medio|bajo
- Puntaje: `EVIDENCIA=x ALCANCE=y RIESGO_DECISION=z REVERSIBILIDAD=w SCORE_DUDA=n`
```

Si el archivo no existe, crearlo.
Mantener solo preguntas activas.

Prohibido registrar duda sin opciones ni puntaje.

## Integracion con otros skills

- `decision-helper`: resolver dudas arquitectonicas registradas.
- `todo-workflow`: ejecutar certezas y decisiones resueltas.
- `frontend-best-practices-audit` y `skill-backend-code-audit`: usar solo como complemento si el usuario lo pide explicitamente.

## Salida esperada

- Resumen corto de hallazgos.
- Conteo de certezas y dudas.
- Tabla final de clasificacion con puntajes por item.
- Confirmacion de ejecucion secuencial:
  - `decision-helper` ejecutado.
  - `todo-workflow` ejecutado.
