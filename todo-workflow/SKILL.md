---
name: todo-workflow
description: "Workflow de procesamiento AUTOMATIZADO de tareas pendientes. Ejecuta certezas y dudas de bajo nivel SIN INTERRUPCIÓN, escala dudas de alto nivel a docs/decision/questions.md. GARANTIZA que docs/todo.md quede VACÍO al finalizar. Usar cuando se requiera procesar completamente el backlog de tareas."
---


# Todo Workflow Skill - Modo Autónomo

Procesa **TODAS** las tareas de `docs/todo.md` de forma automatizada:
- ✅ **Certezas**: Ejecuta inmediatamente sin consultar
- ✅ **Dudas Bajo Nivel**: Evalúa opciones, decide, ejecuta la mejor
- 🔴 **Dudas Alto Nivel**: Mueve a `docs/decision/questions.md` y elimina de `docs/todo.md`

**GARANTÍA**: Al finalizar, `docs/todo.md` debe quedar vacío (solo sección de tareas pendientes sin items).

---

## Flujo de Trabajo Autónomo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INICIO: Leer docs/todo.md                                                  │
│     ↓                                                                       │
│  Para CADA tarea pendiente:                                                 │
│     ├─→ ¿Es CERTEZA?                                                        │
│     │       └─→ EJECUTAR inmediatamente (sin consultar)                    │
│     │       └─→ Mover a docs/todo.done.md                                  │
│     │                                                                       │
│     ├─→ ¿Es DUDA BAJO NIVEL?                                                │
│     │       └─→ EVALUAR opciones (tabla Pros/Contras)                      │
│     │       └─→ DECIDIR mejor opción (agente decide)                       │
│     │       └─→ EJECUTAR la recomendación (sin consultar)                  │
│     │       └─→ Mover a docs/todo.done.md con decisión documentada         │
│     │                                                                       │
│     └─→ ¿Es DUDA ALTO NIVEL?                                                │
│             └─→ REGISTRAR en docs/decision/questions.md      │
│             └─→ ELIMINAR de docs/todo.md                                   │
│             └─→ (La duda se resolverá manualmente después)                 │
│     ↓                                                                       │
│  FIN: docs/todo.md debe estar VACÍO                                        │
│     ↓                                                                       │
│  Commit con todos los cambios                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Comportamiento por Tipo de Tarea

### 🔵 CERTEZAS - Ejecución Inmediata

**Criterio**: Scope claro, archivo identificado, cambio mecánico, riesgo bajo

**Acción**:
1. Ejecutar el cambio directamente
2. Validar con `npm run quality:fast`
3. Mover a `docs/todo.done.md`
4. Eliminar de `docs/todo.md`

**NO consultar al usuario**.

**Ejemplo**:
```
Tarea: "Migrar color #ff8c00 a token"
→ Ejecutar reemplazo
→ Validar
→ Mover a done.md
→ Eliminar de todo.md
```

---

### 🟡 DUDAS DE BAJO NIVEL - Evaluar y Ejecutar

**Criterio**: Opciones técnicas claras, impacto localizado, riesgo medio/bajo

**Acción**:
1. **Evaluar** opciones en tabla Pros/Contras
2. **Decidir** la mejor opción (agente decide basado en criterios)
3. **Ejecutar** la opción recomendada
4. **Documentar** decisión en `docs/todo.done.md`
5. **Eliminar** de `docs/todo.md`

**NO consultar al usuario** - el agente decide y ejecuta.

**Ejemplo**:
```
Tarea: "¿Usar flex o grid para layout?"
→ Evaluar:
   | Opción | Pros | Contras |
   | A. Flex | Simple, responsive | Menos control 2D |
   | B. Grid | Control 2D | Más complejo |
→ Decidir: Opción A (Flex) - justificación: simplicidad
→ Ejecutar cambio a flex
→ Documentar decisión en done.md
→ Eliminar de todo.md
```

---

### 🔴 DUDAS DE ALTO NIVEL - Escalar y Eliminar

**Criterio**: Impacto cross-cutting, decisión arquitectónica/estratégica, riesgo alto

**Acción**:
1. **Registrar** en `docs/decision/questions.md`:
   ```markdown
   ### [YYYY-MM-DD] [Título de la pregunta]
   - **Contexto**: [Descripción del contexto]
   - **Pregunta**: [La duda específica]
   - **Opciones consideradas**: [Lista de alternativas]
   - **Decisión**: (pendiente - escalado desde todo.md)
   - **ADR resultante**: (pendiente)
   ```
2. **ELIMINAR** completamente de `docs/todo.md`
3. **NO ejecutar** ningún cambio (esperará decisión del usuario)

**La tarea desaparece de `todo.md` pero queda registrada en `docs/decision/questions.md`.**

**Ejemplo**:
```
Tarea: "¿Migrar de Vuex a Pinia?"
→ NO ejecutar
→ Registrar en docs/decision/questions.md
→ Eliminar de todo.md
→ (El usuario decidirá más tarde)
```

---

## Reglas de Oro

### 1. `docs/todo.md` debe quedar VACÍO

Después de ejecutar el skill, `docs/todo.md` debe contener solo:

```markdown
# Agenda de Tareas Frontend (`docs/todo.md`)

Backlog activo. Las tareas cerradas se registran en `docs/todo.done.md`.

## Tareas Pendientes

*No hay tareas activas actualmente.*

## Dudas de Alto Nivel (Registradas en docs/decisions/)

Ver `docs/decision/questions.md` para decisiones arquitectónicas pendientes.
```

### 2. Toda tarea procesada debe tener destino

| Tipo | Destino | Estado en todo.md |
|------|---------|-------------------|
| Certeza ejecutada | `docs/todo.done.md` | ELIMINADA |
| Duda bajo nivel ejecutada | `docs/todo.done.md` + decisión documentada | ELIMINADA |
| Duda alto nivel | `docs/decision/questions.md` (solo activas) | ELIMINADA |

**NINGUNA tarea puede quedar en `docs/todo.md` al finalizar.**

### 3. Decisiones de bajo nivel son del agente

Cuando una tarea es "duda de bajo nivel", el agente:
- Evalúa objetivamente las opciones
- Elige la mejor basada en:
  - Menor riesgo
  - Mayor beneficio
  - Consistencia con el codebase existente
  - Mejores prácticas de la industria
- Ejecuta sin consultar
- Documenta la decisión (para que el usuario entienda por qué)

### 4. Dudas de alto nivel NO se ejecutan

Si hay duda sobre si algo es "bajo" o "alto" nivel, **errar por el lado seguro**:
- Si impacta >3 archivos → ALTO NIVEL
- Si cambia contratos/APIs públicas → ALTO NIVEL
- Si afecta múltiples capas → ALTO NIVEL
- Si hay incertidumbre → ALTO NIVEL

**Mejor escalar a docs/decision/questions.md que ejecutar algo riesgoso.**

---

## Proceso Detallado

### Paso 1: Lectura y Clasificación Automática

```markdown
## Análisis de Tareas en docs/todo.md

### CERTEZAS (Ejecutar inmediatamente)
- [ ] Tarea X: [descripción]
  - Archivo: [ruta]
  - Cambio: [específico]

### DUDAS BAJO NIVEL (Evaluar → Decidir → Ejecutar)
- [ ] Tarea Y: [descripción]
  - Opción A: [pros/contras]
  - Opción B: [pros/contras]
  - Decisión: [A/B] - [justificación breve]

### DUDAS ALTO NIVEL (Escalar a docs/decision/questions.md)
- [ ] Tarea Z: [descripción]
  - Impacto: [por qué es alto nivel]
  - Acción: Registrar y eliminar de todo.md
```

### Paso 2: Ejecución Automática

#### Para CERTEZAS:
```
Ejecutando: [descripción]
Archivo: [ruta]
Cambio: [detalle]
Validando...
✅ Pasó quality:fast
Moviendo a done.md...
Eliminando de todo.md...
✅ Completo
```

#### Para DUDAS BAJO NIVEL:
```
Evaluando: [descripción]

| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| A | ... | ... | ✅ |
| B | ... | ... | ❌ |

Justificación: [por qué se eligió A]

Ejecutando Opción A...
Validando...
✅ Pasó quality:fast
Moviendo a done.md con documentación de decisión...
Eliminando de todo.md...
✅ Completo
```

#### Para DUDAS ALTO NIVEL:
```
Escalando: [descripción]
Impacto: [explicación]

Registrando en docs/decision/questions.md (solo pendiente activa)...
Eliminando de docs/todo.md...
✅ Completo (pendiente decisión del usuario)
```

### Paso 3: Verificación de Vaciamiento

Después de procesar TODAS las tareas:

```bash
# Verificar que todo.md está vacío
grep -c "^- \[ \]" docs/todo.md || echo "0 tareas pendientes"

# Debe retornar 0
```

Si quedan tareas → **ERROR**: Reclasificar y procesar.

### Paso 4: Commit Automático

```bash
git add docs/todo.md docs/todo.done.md docs/decisions/
git commit -m "workflow: procesar todas las tareas pendientes

- Ejecutar [N] certezas automáticamente
- Evaluar y ejecutar [N] dudas de bajo nivel
- Escalar [N] dudas de alto nivel a docs/decision/questions.md
- docs/todo.md vaciado completamente

Tareas ejecutadas:
- [lista breve de tareas principales]"
```

---

## Criterios de Decisión para Dudas Bajo Nivel

Cuando el agente debe decidir entre opciones:

### Prioridad de Criterios

1. **Seguridad** > Todo lo demás
   - Opción más segura gana

2. **Simplicidad** > Complejidad
   - Opción más simple que funciona
   - No sobre-ingeniería

3. **Consistencia** > Innovación
   - Igualar patrones existentes en el codebase
   - No introducir excepciones

4. **Mantenibilidad** > Velocidad inicial
   - Código más fácil de mantener
   - Mejor para el equipo a largo plazo

5. **Performance** (solo si es crítico)
   - Solo si hay diferencia significativa medible

### Ejemplos de Decisiones

| Situación | Opción A | Opción B | Decisión | Justificación |
|-----------|----------|----------|----------|---------------|
| ¿Flex o Grid? | Flex (simple) | Grid (potente) | **Flex** | Simplicidad, suficiente para el caso |
| ¿Extraer función o mantener inline? | Extraer | Mantener | **Extraer** | Mantenibilidad, testeabilidad |
| ¿Usar librería X o Y? | X (popular) | Y (moderna) | **X** | Consistencia, más mantenible |

---

## Manejo de Errores

### Si una tarea falla durante ejecución:

1. **Revertir** cambios parciales
2. **Reclasificar** la tarea:
   - ¿Era realmente una certeza? → Cambiar a DUDA ALTO NIVEL
   - ¿Hubo dependencias ocultas? → Cambiar a DUDA ALTO NIVEL
3. **Escalar** a `docs/decision/questions.md`
4. **Documentar** el fallo y por qué se escaló

**NUNCA dejar `docs/todo.md` con tareas fallidas.**

---

## Checklist Final de Ejecución

Antes de considerar el skill completado:

- [ ] `docs/todo.md` está vacío (0 tareas pendientes)
- [ ] Todas las certezas ejecutadas y movidas a `done.md`
- [ ] Todas las dudas bajo nivel evaluadas, ejecutadas y movidas a `done.md`
- [ ] Todas las dudas alto nivel registradas en `docs/decision/questions.md` (solo activas, sin historial)
- [ ] Commit creado con resumen de cambios
- [ ] Validación `quality:fast` pasa

**Resultado esperado**: `docs/todo.md` vacío, backlog completamente procesado.


### 5. `docs/decision/questions.md` NO guarda historial

- Este archivo mantiene **únicamente preguntas activas**.
- Si una pregunta se resuelve vía ADR, debe eliminarse de este archivo.
- No duplicar decisiones resueltas (el historial va en `docs/decisions/ADR-*.md`).

