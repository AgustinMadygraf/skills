---
name: frontend-testing-vue-ts-tailwind
description: "Skill especializado en testing frontend para proyectos con Vue 3, TypeScript y Tailwind. Se usa para crear o corregir tests de componentes, composables y flujos UI con Vitest, Testing Library y Playwright; validar accesibilidad, responsive y estados visuales; y evitar pruebas fr\u00e1giles acopladas a clases de Tailwind o detalles internos de Vue. El resultado del an\u00e1lisis o la ejecucion debe quedar reflejado en docs/todo.md."
---


# Frontend Testing Vue TS Tailwind

Skill especializado para testing de frontend en este stack:

- Vue 3
- TypeScript estricto
- Tailwind CSS
- Vitest
- Testing Library
- Playwright

## Cu\u00e1ndo usarlo
Si el pedido es general de testing pero el stack es Vue 3 + TypeScript + Tailwind, este skill tiene precedencia sobre `testing-general`.

Usar este skill cuando el usuario pida:

- tests unitarios o de integraci\u00f3n para componentes Vue,
- tests de composables,
- pruebas de formularios, validaciones y navegaci\u00f3n,
- cobertura de estados visuales y responsive,
- diagn\u00f3stico de tests UI fr\u00e1giles,
- pruebas smoke/e2e de flujos frontend,
- mejoras de testing para accesibilidad visible y sem\u00e1ntica.

## Contexto del repo

En este proyecto los comandos relevantes son:

- `npm run test`
- `npm run test:coverage`
- `npm run test:e2e`
- `npm run test:e2e:smoke`
- `npm run test:a11y`
- `npm run lint:testing`
- `npm run typecheck`

Los tests viven principalmente en:

- `tests/unit`
- `tests/e2e`
- `tests/setup.ts`

## Modo de operacion

Este skill no debe limitarse a responder en chat.

- Si detecta gaps o deuda de testing frontend, debe registrarlos en `docs/todo.md`.
- Si implementa tests, debe dejar en `docs/todo.md` los pendientes remanentes o riesgos no cubiertos.
- Si no quedan pendientes relevantes, debe indicarlo explicitamente y dejar `docs/todo.md` consistente con ese estado.

## Principios

### 1. Probar como usuario, no como framework

Para componentes Vue, preferir Testing Library y consultas sem\u00e1nticas:

- `getByRole`
- `getByLabelText`
- `getByText`

Evitar depender de:

- estructura exacta del DOM sin necesidad,
- nombres de clases de Tailwind,
- implementaciones internas de `ref`, `computed`, `watch`,
- snapshots grandes de markup.

### 2. Separar niveles

- `unit`: reglas puras, mappers, helpers, validadores.
- `component/integration`: render + eventos + props + emits + dependencias mockeadas en el borde.
- `e2e/smoke`: routing, formularios cr\u00edticos, integraci\u00f3n visible entre pantallas.

### 3. Tailwind no es la API del test

No usar clases Tailwind como contrato principal del test salvo que la clase represente un requerimiento real no observable de otra forma.

Preferir verificar:

- texto visible,
- roles y nombres accesibles,
- estados disabled/loading/error,
- presencia o ausencia de secciones,
- navegaci\u00f3n,
- atributos sem\u00e1nticos relevantes.

Si hay que verificar dise\u00f1o o responsive, hacerlo con:

- expectativas sobre comportamiento visible,
- pruebas e2e en viewport relevante,
- checks de a11y o layout cuando aporten se\u00f1al real.

## Flujo de trabajo

### 1. Leer el componente y su superficie p\u00fablica

Identificar:

- props,
- emits,
- slots,
- side effects,
- dependencias externas,
- estados visibles para el usuario.

### 2. Definir matriz de estados

Cubrir como m\u00ednimo:

- estado inicial,
- carga,
- \u00e9xito,
- error,
- interacciones principales,
- casos de borde si cambian lo visible o la navegaci\u00f3n.

### 3. Elegir herramienta

- `Vitest` para l\u00f3gica y composables.
- `@testing-library/vue` para componentes y formularios.
- `Playwright` para smoke y flujos cr\u00edticos end-to-end.
- `test:a11y` cuando el cambio pueda afectar accesibilidad o estructura visual.

### 4. Mockear con disciplina

Mockear:

- gateways,
- storage,
- analytics,
- router solo si el nivel del test lo justifica.

No mockear Vue internamente.
No mockear tanto que el test deje de representar el flujo real.

### 5. Verificar responsive y Tailwind con criterio

Cuando el cambio afecte layout o breakpoints:

- agregar smoke e2e en viewport representativo,
- verificar que el contenido siga accesible y accionable,
- evitar asserts fr\u00e1giles sobre listas largas de clases utilitarias.

### 6. Ejecutar checks del repo

Secuencia sugerida:

1. `npm run test`
2. `npm run typecheck`
3. `npm run test:e2e:smoke` si el cambio toca flujo UI
4. `npm run test:a11y` si afecta estructura visible o navegaci\u00f3n

Usar `npm run lint:testing` cuando convenga validar cobertura + smoke de forma integrada.

## Anti-patrones

- usar `wrapper.vm` o detalles internos como primera opci\u00f3n,
- assertions masivas sobre HTML serializado,
- acoplar tests a clases `sm:`, `md:`, `lg:` sin motivo funcional,
- mocks globales opacos dif\u00edciles de leer,
- tests que validan una sola implementation detail por archivo,
- no cubrir estados de error en formularios o requests.

## Patr\u00f3n de respuesta

Cuando este skill se active:

1. Explicar qu\u00e9 comportamiento visible o riesgo UI se quiere cubrir.
2. Elegir el nivel de prueba correcto.
3. Implementar tests con consultas sem\u00e1nticas y baja fragilidad.
4. Ejecutar los comandos del repo que apliquen.
5. Actualizar `docs/todo.md` con gaps, follow-ups o riesgos remanentes.
6. Reportar cobertura funcional, gaps y riesgos remanentes.

## Formato esperado en docs/todo.md

Registrar tareas orientadas a comportamiento visible y riesgo UI. Ejemplos:

- [ ] Agregar tests de componente para `QuotePage.vue` cubriendo errores 422 y 429 mostrados al usuario
- [ ] Agregar smoke e2e para `/cotizador/:quoteId/web` con y sin snapshot disponible
- [ ] Revisar asserts fragiles acoplados a clases Tailwind y migrarlos a consultas semanticas

