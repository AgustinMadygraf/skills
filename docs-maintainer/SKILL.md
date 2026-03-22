---
name: docs-maintainer
description: "Skill especializado en mantener, sincronizar y optimizar toda la documentación del proyecto en docs/. Gestiona todo.md, todo.done.md, ADRs, docs/decision/questions.md y genera índices automáticos. Detecta inconsistencias, duplicaciones y oportunidades de mejora en la documentación técnica. Modo preventivo: solo detecta y propone cambios, no modifica sin confirmación."
---


# Docs Maintainer - Mantenimiento de Documentación

Skill especializado para gestionar, sincronizar y optimizar toda la documentación técnica del proyecto en `docs/`.

## Responsabilidades

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. MANTENER docs/todo.md                                                   │
│  ├─→ Estructura consistente                                                │
│  ├─→ Categorías correctas (CRÍTICO/ADVERTENCIA/MEJORA)                     │
│  ├─→ Enlaces funcionales                                                   │
│  └─→ Sin tareas duplicadas                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. CONSOLIDAR docs/todo.done.md                                            │
│  ├─→ Orden cronológico                                                     │
│  ├─→ Sin duplicaciones                                                     │
│  ├─→ Referencias a ADRs completas                                          │
│  └─→ Resumen ejecutivo actualizado                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. GESTIONAR ADRs                                                          │
│  ├─→ Numeración secuencial correcta                                        │
│  ├─→ Índice automático en decisions/README.md                              │
│  ├─→ Links entre ADRs relacionados                                         │
│  └─→ Estado actualizado (Aceptada/Implementada/Completada)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SINCRONIZAR docs/decision/questions.md                                   │
│  ├─→ Solo preguntas activas                                                │
│  ├─→ Referencias a ADRs resultantes                                        │
│  ├─→ Sin historial (solo inbox)                                            │
│  └─→ Estado pendiente/documentado                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. GENERAR REPORTES                                                        │
│  ├─→ Métricas de deuda técnica                                             │
│  ├─→ Estado de decisiones arquitectónicas                                  │
│  ├─→ Progreso de tareas                                                    │
│  └── Índices y navegación                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INICIO: Activación del Docs Maintainer                                     │
│     ↓                                                                       │
│  1. AUDITAR ESTRUCTURA DE docs/                                             │
│     ├─→ Verificar archivos requeridos existen                              │
│     ├─→ Detectar archivos huérfanos (sin referencias)                      │
│     ├─→ Identificar duplicaciones                                          │
│     └─→ Validar formato markdown                                           │
│     ↓                                                                       │
│  2. SINCRONIZAR TODO FILES                                                  │
│     ├─→ Ordenar todo.done.md cronológicamente                              │
│     ├─→ Eliminar duplicaciones                                             │
│     ├─→ Verificar coherencia entre todo.md y done.md                       │
│     └─→ Consolidar múltiples archivos done si existen                      │
│     ↓                                                                       │
│  3. GESTIONAR ADRs                                                          │
│     ├─→ Generar índice en decisions/README.md                              │
│     ├─→ Verificar numeración secuencial                                    │
│     ├─→ Detectar ADRs sin implementar                                      │
│     └─→ Actualizar estados si es necesario                                 │
│     ↓                                                                       │
│  4. VALIDAR LINKS Y REFERENCIAS                                             │
│     ├─→ Verificar links a archivos existen                                 │
│     ├─→ Detectar referencias rotas                                         │
│     ├─→ Validar links a ADRs                                               │
│     └─→ Verificar referencias cruzadas                                     │
│     ↓                                                                       │
│  5. GENERAR REPORTE DE ESTADO                                               │
│     ├─→ Métricas de documentación                                          │
│     ├── Deuda técnica documentada                                          │
│     ├─→ Decisiones pendientes                                              │
│     └─→ Recomendaciones de mejora                                          │
│     ↓                                                                       │
│  FIN: Propuesta de cambios al usuario                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Archivos Gestionados

### Core Files (Requeridos)
- `docs/todo.md` - Backlog activo
- `docs/todo.done.md` - Historial de tareas completadas
- `docs/decision/questions.md` - Decisiones pendientes
- `docs/decisions/README.md` - Índice de ADRs (generado)

### ADRs (Decisiones Documentadas)
- `docs/decisions/ADR-NNN-*.md` - Architecture Decision Records
- Numeración secuencial
- Estado actualizado
- Referencias cruzadas

### Opcionales
- `docs/*.md` - Otros documentos técnicos
- `docs/**/*.md` - Subdocumentación

## Checklist de Mantenimiento

### Estructura
- [ ] `docs/todo.md` existe y tiene formato correcto
- [ ] `docs/todo.done.md` existe y está ordenado
- [ ] `docs/decisions/` existe con README.md
- [ ] No hay archivos markdown huérfanos

### Contenido todo.md
- [ ] Tiene sección "Tareas Pendientes"
- [ ] Tiene sección "Dudas de Alto Nivel"
- [ ] Categorías correctas: 🔴 CRÍTICO / 🟡 ADVERTENCIA / 🟢 MEJORA
- [ ] Tareas tienen formato accionable
- [ ] No hay tareas duplicadas

### Contenido todo.done.md
- [ ] Orden cronológico (más reciente primero)
- [ ] Fechas en formato [YYYY-MM-DD]
- [ ] Referencias a ADRs completas
- [ ] Sin entradas duplicadas
- [ ] Resumen de decisiones actualizado

### ADRs
- [ ] Numeración secuencial sin gaps
- [ ] Índice en decisions/README.md
- [ ] Estado correcto: Propuesta/Aceptada/Implementada/Completada
- [ ] Fecha de decisión presente
- [ ] Links a ADRs relacionados funcionan

### Preguntas Arquitectura
- [ ] Solo contiene preguntas activas
- [ ] Sin historial (eliminadas las resueltas)
- [ ] Referencias a ADRs si están resueltas
- [ ] Estado: (pendiente) o (decidida)

## Reportes Generados

### Reporte de Estado de Documentación

```markdown
## Estado de Documentación - 2026-03-09

### Métricas
| Métrica | Valor | Estado |
|---------|-------|--------|
| Tareas pendientes | 0 | ✅ OK |
| Tareas completadas (total) | 45 | ✅ OK |
| ADRs activos | 9 | ✅ OK |
| Preguntas pendientes | 0 | ✅ OK |
| Archivos huérfanos | 0 | ✅ OK |

### ADRs por Estado
| Estado | Cantidad |
|--------|----------|
| Aceptada | 9 |
| En implementación | 0 |
| Completada | 9 |

### Recomendaciones
- ✅ Documentación sincronizada
- ✅ Sin acciones requeridas
```

### Reporte de Deuda Técnica

```markdown
## Deuda Técnica Documentada

### Componentes Grandes (>600 líneas)
1. HomePage.vue (1,276) - ADR-003 ✅
2. ContactFormSection.vue (641) - ADR-004 ✅
3. QuotePage.vue (601) - ADR-009 ✅

### TODOs en Código
- `src/ui/pages/quoteWebState.ts:1` - Migrar a features/quote/ui
- `src/ui/features/contact/ContactFormSection.vue:20` - Mover a features/contact/ui

### SOLID-DEBATEs
- `src/ui/pages/HomePage.ts:15` - Tercera variante
- `src/ui/pages/QuotePage.vue:34` - Workflow composable
```

## Heurísticas de Detección

### Archivo Huérfano
```
🔍 CRITERIO: Archivo markdown en docs/ que:
- No está referenciado en ningún otro archivo
- No es el índice (README.md)
- No tiene inbound links

✅ ACCIÓN: Mover a docs/archive/ o eliminar
```

### Tarea Duplicada
```
🔍 CRITERIO: Dos tareas en todo.md que:
- Mencionan el mismo archivo
- Describen el mismo problema
- Tienen solapamiento >70%

✅ ACCIÓN: Consolidar en una sola tarea
```

### ADR sin Implementar
```
🔍 CRITERIO: ADR con estado "Aceptada" pero:
- No hay tareas en todo.md relacionadas
- No hay referencias en código (comentarios)
- Fecha > 30 días

✅ ACCIÓN: Crear tareas en todo.md o actualizar estado
```

### Numeración ADR Incorrecta
```
🔍 CRITERIO: ADRs con gaps en numeración:
- ADR-001, ADR-002, ADR-004 (falta ADR-003)
- ADRs con mismo número

✅ ACCIÓN: Renumerar manteniendo referencias
```

## Modos de Operación

### Modo 1: Auditoría Completa (Recomendado)
```
"Ejecuta el docs-maintainer"
```
Audita toda la documentación, detecta problemas, propone cambios.

### Modo 2: Solo Sincronizar TODO
```
"Sincroniza docs/todo.md y todo.done.md"
```
Ordena, elimina duplicaciones, consolida.

### Modo 3: Solo Gestionar ADRs
```
"Genera índice de ADRs"
```
Actualiza decisions/README.md, verifica numeración.

### Modo 4: Solo Validar Links
```
"Valida links en docs/"
```
Detecta referencias rotas, links huérfanos.

## Integración con Orchestrator

El `docs-maintainer` es llamado por el `skill-frontend-orchestrator` y por el `skill-backend-orchestrator` como parte del flujo completo:

```
skill-frontend-orchestrator/
  ├─→ clean-architecture-orchestrator ──▶ hallazgos ──▶ docs/todo.md
  ├─→ frontend-best-practices-audit ──▶ hallazgos ──▶ docs/todo.md
  ├─→ todo-workflow ──▶ procesa tareas
  └─→ docs-maintainer ──▶ sincroniza documentación
       ├─→ Ordena todo.done.md
       ├─→ Genera índice ADRs
       └─→ Valida links
```

## Output del Skill

### Propuesta de Cambios

```markdown
## Propuesta de Mantenimiento de Documentación

### Cambios Sugeridos

#### 1. Reordenar todo.done.md
- Entradas desordenadas entre [2026-03-08] y [2026-03-09]
- Acción: Ordenar cronológicamente

#### 2. Generar índice ADRs
- Falta decisions/README.md
- Acción: Crear índice automático

#### 3. Eliminar duplicación
- Tarea "Agregar :key a v-for" aparece 2 veces en todo.done.md
- Acción: Consolidar en una entrada

### Validaciones Previas
- ✅ TypeScript: Sin errores
- ✅ Links: Todos funcionan
- ✅ Formato: Markdown válido

### ¿Aplicar cambios?
[Confirmar] [Cancelar] [Ver detalles]
```

## Reglas de Oro

1. **No Modificar sin Confirmar**
   - Detectar y proponer, no ejecutar automáticamente
   - El usuario decide qué cambios aplicar

2. **Preservar Historial**
   - Nunca eliminar entradas de todo.done.md
   - Archivar en lugar de borrar

3. **Consistencia Primero**
   - Formato uniforme en todos los archivos
   - Convenciones de naming consistentes

4. **Transparencia**
   - Todo cambio queda registrado
   - Justificación clara para cada propuesta

## Uso del Skill

```bash
# Modo completo
"Ejecuta el docs-maintainer"

# Modos específicos
"Sincroniza docs/todo.md"
"Genera índice de ADRs"
"Valida links en documentación"
```

## Dependencias

- **skills**: Ninguna (skill independiente)
- **herramientas**: grep, find, wc (básicas)
- **archivos**: docs/**/*.md

## Estado del Skill

- **Versión**: 1.0.0
- **Estado**: Activo
- **Última actualización**: 2026-03-09
- **Creado para**: Completar ecosistema de skills de automatización

