---
name: decision-helper
description: "Asistente para la toma de decisiones arquitectónicas. Lee docs/decision/questions.md, selecciona la pregunta más importante (por prioridad o FIFO si empate), analiza el contexto completo, y proporciona información estructurada para que el usuario tome una decisión informada. En casos obvios y de bajo riesgo, puede decidir autónomamente. Tras la decisión, genera ADR completo, actualiza docs/todo.md con plan de acción, y elimina la pregunta de pendientes. Finalmente, indica activación de todo-workflow. Usar cuando haya decisiones arquitectónicas pendientes que requieran análisis y resolución."
---


# Decision Helper Skill

Asistente especializado para la toma de decisiones arquitectónicas. Transforma preguntas pendientes en decisiones documentadas y accionables.

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. LEER docs/decision/questions.md                          │
│     ↓                                                                       │
│  2. SELECCIONAR pregunta más importante                                     │
│     ├─→ Evaluar cada pregunta por:                                          │
│     │   • Impacto (1-5): ¿Cuánto afecta al sistema?                         │
│     │   • Urgencia (1-5): ¿Qué tan pronto se necesita?                      │
│     │   • Riesgo (1-5): ¿Qué tan arriesgado es no decidir?                  │
│     │   • Bloqueo: ¿Bloquea otras tareas?                                   │
│     ├─→ Calcular score: (Impacto × Urgencia) / Riesgo                       │
│     └─→ Si empate: Elegir la más antigua (FIFO)                             │
│     ↓                                                                       │
│  3. ANALIZAR contexto completo                                              │
│     ├─→ Leer archivos relacionados mencionados en la pregunta              │
│     ├─→ Identificar stakeholders afectados                                  │
│     ├─→ Evaluar opciones consideradas                                      │
│     └→ Detectar dependencias y consecuencias                                │
│     ↓                                                                       │
│  4. PRESENTAR análisis al usuario                                          │
│     ├─→ Resumen ejecutivo                                                   │
│     ├─→ Contexto completo                                                   │
│     ├─→ Análisis de opciones (Pros/Contras detallados)                     │
│     ├─→ Recomendación del agente (si aplica)                               │
│     └→ Riesgos de cada opción                                               │
│     ↓                                                                       │
│  5. TOMA DE DECISIÓN                                                        │
│     ├─→ ¿Es caso obvio y de bajo riesgo?                                   │
│     │   ├─→ SÍ: Decidir autónomamente → Proceder al paso 6                 │
│     │   └─→ NO: Consultar usuario → Esperar decisión → Proceder al paso 6  │
│     ↓                                                                       │
│  6. DOCUMENTAR decisión                                                     │
│     ├─→ Crear ADR completo en docs/                                         │
│     ├─→ Actualizar docs/todo.md con plan de acción                         │
│     ├─→ Eliminar la pregunta de docs/decision/questions.md          │
│     └→ Referenciar ADR resultante                                           │
│     ↓                                                                       │
│  7. ACTIVAR todo-workflow (indicar al usuario)                             │
│     └─→ "Ejecutar: skill:todo-workflow"                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Criterios de Priorización

### Matriz de Evaluación

Para cada pregunta, calcular:

```
Score = (Impacto × Urgencia × Bloqueo) / Riesgo

Donde:
- Impacto: 1 (mínimo) a 5 (transformacional)
- Urgencia: 1 (baja) a 5 (crítica/inmediata)
- Bloqueo: 1 (no bloquea) a 3 (bloquea múltiples tareas)
- Riesgo: 1 (bajo) a 5 (crítico)
```

### Desempate

Si dos preguntas tienen el mismo score:
1. **Elegir la más antigua** (FIFO)
2. Si misma fecha: Elegir la primera en el archivo

## Análisis de Contexto

### Información a Recopilar

1. **Archivos mencionados**: Leer código relevante
2. **Dependencias**: ¿Qué otros componentes se ven afectados?
3. **Historial**: ¿Hay decisiones similares previas en docs/decisions/?
4. **Restricciones**: Técnicas, de negocio, de tiempo
5. **Oportunidades**: ¿Esta decisión habilita otras mejoras?

### Formato de Presentación

```markdown
## 📊 Análisis de Decisión Arquitectónica

### Pregunta Seleccionada
**[Título de la pregunta]**
- Fecha de registro: [YYYY-MM-DD]
- Score de prioridad: [X.XX]

### Contexto Completo
[Descripción detallada del problema, por qué surgió, contexto técnico y de negocio]

### Análisis de Opciones

#### Opción A: [Descripción]
**Pros:**
- [Beneficio 1]
- [Beneficio 2]

**Contras:**
- [Desventaja 1]
- [Desventaja 2]

**Riesgos:** [Alto/Medio/Bajo]
**Esforzo:** [Alto/Medio/Bajo]

#### Opción B: [Descripción]
[...]

### Recomendación del Agente
**Opción recomendada**: [X]

**Justificación**:
[Por qué esta opción es la mejor basada en los criterios de evaluación]

**Riesgo residual**: [Descripción]

---

**¿Confirmas esta decisión o prefieres otra opción?**
**¿Necesitas más información sobre algún aspecto?**
```

## Toma de Decisión Autónoma

### Cuándo Decidir Autónomamente

El skill PUEDE decidir solo cuando:
- ✅ Riesgo es BAJO (1-2)
- ✅ Impacto es LOCALIZADO (no cross-cutting)
- ✅ Una opción es CLARAMENTE superior
- ✅ No hay dependencias complejas
- ✅ Decisión es reversible fácilmente

### Cuándo Consultar al Usuario

El skill DEBE consultar cuando:
- 🔴 Riesgo es ALTO (4-5)
- 🔴 Impacto es CROSS-CUTTING (afecta múltiples capas)
- 🔴 Múltiples opciones válidas con trade-offs similares
- 🔴 Hay restricciones de negocio no técnicas
- 🔴 Decisión es irreversible o costosa de revertir

## Documentación Post-Decisión

### 1. Crear ADR Completo

Archivo: `docs/decisions/ADR-XXX-[nombre-decision].md`

```markdown
# ADR-XXX: [Título de la Decisión]

## Estado
- **Fecha**: [YYYY-MM-DD]
- **Estado**: Aceptada / En implementación / Completada
- **Decisores**: [Usuario/Agente/Equipo]

## Contexto
[Descripción del problema y contexto que llevó a esta decisión]

## Decisión
**Opción seleccionada**: [Letra + Descripción]

**Justificación**:
[Por qué se eligió esta opción sobre las demás]

## Consecuencias

### Positivas
- [Beneficio 1]
- [Beneficio 2]

### Negativas / Trade-offs
- [Compromiso 1]
- [Compromiso 2]

## Alternativas Rechazadas

### Opción [X]: [Descripción]
**Por qué se rechazó**:
[Justificación]

### Opción [Y]: [Descripción]
**Por qué se rechazó**:
[Justificación]

## Implementación
- **Plan de acción**: Ver docs/todo.md (tarea #[N])
- **Fecha estimada**: [YYYY-MM-DD]
- **Responsable**: [Asignado]

## Notas
[Información adicional, referencias, enlaces útiles]
```

### 2. Actualizar docs/todo.md

```markdown
# Agenda de Tareas Frontend (`docs/todo.md`)

## Implementación de Decisión Arquitectónica

### [ADR-XXX] [Título breve de la decisión]
- [ ] Paso 1: [Acción específica]
  - **Archivo**: `[ruta]`
  - **Cambio**: [Descripción técnica]
  
- [ ] Paso 2: [Acción específica]
  - **Archivo**: `[ruta]`
  - **Cambio**: [Descripción técnica]

- [ ] Validar implementación
  - `npm run quality:fast`
  - Tests específicos

**Referencia**: `docs/decisions/ADR-XXX-[nombre].md`
**Prioridad**: [Alta/Media/Baja]
**Estimación**: [X horas/días]
```

### 3. Actualizar docs/decision/questions.md

Eliminar la pregunta de la sección de activas (no mantener historial en este archivo):

```markdown
### [YYYY-MM-DD] [Título de la pregunta]
- **Contexto**: [Descripción]
- **Pregunta**: [La duda específica]
- **Opciones consideradas**: [Lista]
- **Decisión**: [Opción seleccionada + fecha]
- **ADR resultante**: `docs/decisions/ADR-XXX-[nombre].md`
- **Implementación**: Ver docs/todo.md
```

## Activación de todo-workflow

Tras completar la documentación, el skill debe indicar:

```
✅ Decisión documentada y plan de acción creado

📋 SIGUIENTE PASO: Ejecutar skill:todo-workflow
   El plan de acción está en docs/todo.md listo para ser procesado.
   
   Comando: skill:todo-workflow
   
   Esto procesará automáticamente las tareas de implementación
   según el workflow de decisiones (certezas/dudas/alto nivel).
```

## Ejemplo de Flujo Completo

### Entrada
```markdown
### [2026-03-08] Seguridad - Uso de innerHTML en Microsoft Clarity
- **Contexto**: innerHTML detectado en clarity.ts
- **Pregunta**: ¿Cómo mitigar el riesgo?
- **Opciones**: A) Mantener, B) Cambiar a script src, C) CSP nonce, D) Reemplazar
- **Decisión**: (pendiente)
```

### Análisis del Skill
```markdown
Score: (3 × 2 × 1) / 2 = 3.0

Contexto: Código de terceros (Microsoft), riesgo real bajo,
pero potencial vector XSS. Opciones claras con trade-offs definidos.

Recomendación: Opción A (documentar) por simplicidad y riesgo bajo.
```

### Decisión (Autónoma - caso obvio)
```markdown
Decisión: Opción A - Mantener con comentario explicativo
Justificación: Riesgo bajo (código Microsoft estático), 
cambio innecesario, documentación suficiente.
```

### Salida
1. **ADR creado**: `docs/decisions/ADR-001-clarity-innerhtml.md`
2. **docs/todo.md**: Tarea para agregar comentario explicativo
3. **docs/decision/questions.md**: Eliminada de activas
4. **Instrucción**: "Ejecutar: skill:todo-workflow"

## Checklist de Ejecución

- [ ] Leer docs/decision/questions.md
- [ ] Evaluar todas las preguntas con matriz de prioridad
- [ ] Seleccionar pregunta con mayor score (FIFO si empate)
- [ ] Leer archivos de código relacionados
- [ ] Analizar opciones y consecuencias
- [ ] Presentar análisis estructurado al usuario
- [ ] Tomar decisión (autónoma o consultada)
- [ ] Crear ADR completo
- [ ] Actualizar docs/todo.md con plan de acción
- [ ] Eliminar la pregunta de docs/decision/questions.md
- [ ] Indicar activación de todo-workflow


## Política de `docs/decision/questions.md`

- `docs/decision/questions.md` es **solo inbox de preguntas activas**.
- Una vez tomada la decisión y creado el ADR, la pregunta **se elimina** del archivo.
- El historial oficial vive **únicamente** en `docs/decisions/ADR-*.md`.

