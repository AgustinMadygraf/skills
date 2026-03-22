---
name: frontend-best-practices-audit
description: "Auditoría especializada de mejores prácticas frontend enfocada en Vue 3, TypeScript riguroso, naming conventions, patrones de comunicación HTTP y UI/UX visual. Analiza src/ detectando inconsistencias, malas prácticas, problemas de usabilidad y oportunidades de mejora. Para auditoría de Arquitectura Limpia y SOLID, usar clean-architecture-orchestrator. Modo preventivo: solo lista hallazgos en docs/todo.md sin ejecutar fixes automáticos."
---


# Auditoría de Mejores Prácticas Frontend

Skill especializado para auditoría de código fuente (`src/`) en cinco dimensiones críticas de calidad frontend.

## Alcance de la Auditoría

**Solo código fuente:** `src/` directory

**Incluye:**
- Componentes Vue 3 (.vue)
- Módulos TypeScript (.ts)
- Composables y utilidades
- Estructura de carpetas y naming
- Patrones de comunicación HTTP

**NO incluye:**
- Configuraciones de build
- Dependencias externas (node_modules)
- Assets estáticos
- Tests (salvo malas prácticas evidentes)

## Cinco Pilares de Análisis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Pilar 1: VUE PATTERNS                                                     │
│  ├─ Script setup y Composition API                                         │
│  ├─ Props/Emits tipados con TypeScript                                     │
│  ├─ Composables (naming, ubicación, reutilización)                         │
│  ├─ Reactivity (ref, reactive, computed, watch)                            │
│  └─ Lazy loading y code splitting                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Pilar 2: TYPESCRIPT RIGOROSO                                              │
│  ├─ Uso de any vs unknown                                                  │
│  ├─ Type guards y narrowing                                                │
│  ├─ Generics y utilidades de tipos                                         │
│  ├─ Return types explícitos                                                │
│  └─ Strict mode compliance                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Pilar 3: NAMING & STRUCTURE                                               │
│  ├─ PascalCase vs camelCase vs kebab-case                                  │
│  ├─ Convenciones para composables (useX vs xHooks)                         │
│  ├─ Estructura de features (domain/app/infra/ui)                           │
│  └─ Barrel files (index.ts)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Pilar 4: COMMUNICATION PATTERNS                                           │
│  ├─ Ports & Adapters (HTTP client)                                         │
│  ├─ Error handling y Result types                                          │
│  ├─ Retry logic y timeouts                                                 │
│  ├─ Cancelación de requests                                                │
│  └─ Offline handling                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Pilar 5: UI/UX VISUAL (Integrado desde ui-ux-audit)                       │
│  ├─ Jerarquía visual (títulos, CTAs, espaciado)                            │
│  ├─ Consistencia de interfaz (tokens, estados, componentes)                │
│  ├─ Usabilidad (flujos, mensajes de error, navegación)                     │
│  ├─ Responsive y legibilidad (mobile/desktop, contraste)                   │
│  └─ Accesibilidad percibida (foco, orden visual, contraste)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Nota:** Para auditoría de **Clean Architecture** y **principios SOLID**, usar el skill `clean-architecture-orchestrator`.
> Este skill se enfoca exclusivamente en patrones frontend, TypeScript, naming y UI/UX.

## Metodología: Preventiva

**IMPORTANTE:** Este skill opera en modo **preventivo**:
- 🔴 **NO ejecuta fixes automáticos**
- 🔴 **NO modifica código**
- 🟢 **Solo detecta y lista en `docs/todo.md`**

El usuario decide qué fixes aplicar y cuándo.

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. DISCOVER - Identificar archivos en src/                                │
│     ├─→ Componentes Vue (.vue)                                             │
│     ├─→ Módulos TypeScript (.ts)                                           │
│     ├─→ Composables y utilidades                                           │
│     └─→ Estructura de carpetas                                             │
│     ↓                                                                       │
│  2. ANALYZE - Cinco pasadas de análisis                                    │
│     ├─→ Pasada 1: Vue Patterns                                             │
│     ├─→ Pasada 2: TypeScript Rigoroso                                      │
│     ├─→ Pasada 3: Naming & Structure                                       │
│     ├─→ Pasada 4: Communication Patterns                                   │
│     └─→ Pasada 5: UI/UX Visual                                             │
│     ↓                                                                       │
│  3. CLASSIFY - Clasificar hallazgos                                        │
│     ├─→ 🔴 CRÍTICO: Bugs potenciales, malas prácticas críticas             │
│     ├─→ 🟡 ADVERTENCIA: Inconsistencias, deuda técnica                     │
│     └─→ 🟢 MEJORA: Oportunidades de refactoring                            │
│     ↓                                                                       │
│  4. OUTPUT - Generar docs/todo.md                                          │
│     └─→ Tareas organizadas por pilar y severidad                           │
│     ↓                                                                       │
│  5. REPORT - Resumen al usuario                                            │
│     └─→ Estadísticas, prioridades, recomendaciones                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Categorías de Hallazgos

### 🔴 CRÍTICO - Bugs y Malas Prácticas

**Vue Patterns:**
- Options API mezclado con Composition API sin justificación
- Props no tipadas o con `any`
- Mutación de props directamente
- Side effects en computed sin watchers
- v-for sin :key o con índice como key en listas dinámicas

**TypeScript:**
- Uso innecesario de `any` cuando `unknown` + type guard es posible
- Type assertions (`as Type`) que pueden fallar en runtime
- Funciones sin return type en API públicas
- Desactivación de reglas strict en tsconfig

**Communication:**
- No manejo de errores en llamadas HTTP
- Race conditions en requests concurrentes
- Secrets o datos sensibles en logs

### 🟡 ADVERTENCIA - Inconsistencias

**Naming:**
- PascalCase vs camelCase inconsistente (ej: `contactHooks.ts` vs `ContactFormSection.ts`)
- Composables sin prefijo `use` (ej: `contactHooks` debería ser `useContactHooks`)
- Nombres de archivos que no representan el contenido
- Barrel files que re-exportan sin valor agregado

**Structure:**
- Duplicación de lógica entre `features/x/` y `ui/features/x/`
- Composables en ubicaciones inconsistentes
- Feature modules que no siguen la estructura estándar

**Vue:**
- Components con >600 líneas sin documentar decisión (ADR)
- Props drilling excesivo (>3 niveles)
- Watchers que podrían ser computed

### 🟢 MEJORA - Oportunidades

**TypeScript:**
- Reducir ratio `any`/`unknown` (meta: <5% `any`)
- Agregar type guards para narrowing
- Usar `satisfies` en lugar de `as` cuando sea posible

**Vue:**
- Usar `defineModel` (Vue 3.3+) para v-model custom
- Reemplazar watchers con `watchEffect` cuando sea apropiado
- Extraer lógica a composables cuando se repite 3+ veces

**Communication:**
- Agregar `AbortController` para cancelación de requests
- Implementar retry con backoff exponencial
- Agregar indicadores de loading por operación

## Heurísticas de Detección

### Vue Patterns

```typescript
// 🔴 CRÍTICO: Props no tipadas
const props = defineProps({
  value: { type: String, required: true }  // ❌ Sin TypeScript
})

// ✅ CORRECTO: Props tipadas
interface Props {
  value: string
}
const props = defineProps<Props>()

// 🔴 CRÍTICO: Mutación de props
props.value = 'nuevo'  // ❌ Nunca mutar props

// ✅ CORRECTO: Emitir evento
emit('update:value', 'nuevo')

// 🟡 ADVERTENCIA: Composable sin prefijo use
export function contactHooks() { }  // ❌ Debería ser useContactHooks
```

### TypeScript Rigoroso

```typescript
// 🔴 CRÍTICO: any innecesario
function process(data: any) { }  // ❌ Usar unknown + type guard

// ✅ CORRECTO
function process(data: unknown) {
  if (typeof data === 'string') {
    // narrowing seguro
  }
}

// 🟡 ADVERTENCIA: Type assertion riesgosa
const user = data as User  // ❌ Puede fallar en runtime

// ✅ CORRECTO: Type guard
function isUser(data: unknown): data is User {
  return data && typeof (data as User).id === 'string'
}
```

### Naming Conventions

| Tipo | Convención | Ejemplo |
|------|------------|---------|
| Componentes Vue | PascalCase | `ContactForm.vue` |
| Composables | camelCase con use | `useContactForm.ts` |
| Utilidades | camelCase | `formatDate.ts` |
| Tipos/Interfaces | PascalCase | `ContactFormProps.ts` |
| Constantes | UPPER_SNAKE_CASE | `API_TIMEOUT_MS` |
| Features | kebab-case carpetas | `contact-form/` |

### Communication Patterns

```typescript
// 🔴 CRÍTICO: Sin manejo de errores
try {
  await fetch('/api/data')
} catch (e) {
  console.error(e)  // ❌ Solo log, no hay estrategia
}

// ✅ CORRECTO: Result type
const result = await gateway.fetchData()
if (result.ok) {
  // usar result.value
} else {
  // manejar result.error
}

// 🟡 ADVERTENCIA: Sin timeout ni cancelación
const response = await fetch(url)  // ❌ Puede colgarse

// ✅ CORRECTO: Con timeout y abort
const controller = new AbortController()
const timeout = setTimeout(() => controller.abort(), 10000)
const response = await fetch(url, { signal: controller.signal })
clearTimeout(timeout)
```

## Checklist de Auditoría Completa

### Vue Patterns
- [ ] Todos los componentes usan `<script setup>`
- [ ] Props tipadas con interfaces/types
- [ ] Emits tipados con interfaces
- [ ] Composables usan prefijo `use`
- [ ] v-for con `:key` único (no índice)
- [ ] Lazy loading en router
- [ ] Components >600 líneas tienen ADR

### TypeScript Rigoroso
- [ ] Ratio `any`/`unknown` < 20%
- [ ] Funciones públicas tienen return type
- [ ] Type guards para narrowing
- [ ] Evitar type assertions (`as`)
- [ ] Strict mode habilitado
- [ ] No `// @ts-ignore` sin justificación

### Naming & Structure
- [ ] PascalCase para componentes
- [ ] camelCase para composables (useX)
- [ ] Consistencia en nombres de archivos
- [ ] Barrel files justificados
- [ ] Estructura de features coherente

### Communication Patterns
- [ ] Ports & Adapters implementados
- [ ] Error handling con Result types
- [ ] Timeout en requests HTTP
- [ ] Retry logic configurado
- [ ] Cancelación de requests (AbortController)

### Métricas de Código Frontend
- [ ] Funciones <50 líneas
- [ ] Componentes <600 líneas (o documentado con ADR)
- [ ] Comentarios TODO presentes
- [ ] Comentarios de decisión consciente (SOLID-DEBATE)

> **Nota:** Para auditoría de **Clean Architecture compliance**, usar `clean-architecture-orchestrator` con `npm run lint:layers`.

## Formato de Output en docs/todo.md

```markdown
# Agenda de Tareas Frontend (`docs/todo.md`)

## 🔴 CRÍTICO - Vue/TS Patterns

### Props no tipadas en UserProfile.vue
- [ ] [CRÍTICO] Migrar props a TypeScript strict
  - **Archivo**: `src/ui/components/UserProfile.vue` (línea 23)
  - **Problema**: `defineProps({ value: String })` sin tipado
  - **Riesgo**: Runtime errors, no hay autocomplete
  - **Solución**: Usar `defineProps<Props>()` con interface
  - **Prioridad**: Alta - afecta developer experience

## 🟡 ADVERTENCIA - Naming/Structure

### Inconsistencia naming composables
- [ ] [ADVERTENCIA] Renombrar contactHooks.ts
  - **Archivo**: `src/features/contact/contactHooks.ts`
  - **Problema**: No usa prefijo `use` (convención Vue)
  - **Sugerencia**: Renombrar a `useContactHooks.ts`
  - **Prioridad**: Media - consistencia de codebase

## 🟢 MEJORA - Communication

### Agregar AbortController en quoteApiGateway
- [ ] [MEJORA] Implementar cancelación de requests
  - **Archivo**: `src/infrastructure/quote/quoteApiGateway.ts`
  - **Problema**: Requests no cancelables
  - **Sugerencia**: Agregar signal a fetch options
  - **Prioridad**: Baja - mejora UX
```

## Reglas de Oro

1. **Consistencia > Perfección**
   - Mejor ser consistente que "perfecto" pero inconsistente
   - Seguir convenciones establecidas en el proyecto

2. **Pragmatismo sobre Dogmatismo**
   - Las reglas pueden romperse con justificación documentada
   - Los comentarios SOLID-DEBATE indican decisión consciente

3. **Type Safety es No Negociable**
   - `any` solo cuando no hay alternativa
   - Preferir `unknown` + type guards

4. **Developer Experience Importa**
   - Autocomplete, navegación, legibilidad
   - Naming claro y representativo

## Integración con Otros Skills

- **clean-architecture-orchestrator**: Complementa con seguridad y SOLID
- **decision-helper**: Usar cuando hallazgos requieran decisión arquitectónica
- **todo-workflow**: Procesar tareas generadas por este audit

## Uso del Skill

El usuario activa este skill manualmente cuando necesita:

1. **Onboarding de nuevos desarrolladores**: Mostrar estándares del proyecto
2. **Code review previo**: Identificar issues antes de PR
3. **Refactor planning**: Priorizar deuda técnica
4. **Periódicamente**: Mantener calidad del codebase

**Integración:** Skill independiente. No se activa automáticamente.

