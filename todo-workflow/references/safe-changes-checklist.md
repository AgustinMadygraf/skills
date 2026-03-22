# Checklist de Cambios Seguros

Lista de cambios que pueden ejecutarse automáticamente (modo batch) sin consulta previa.

## ✅ CSS y Diseño

### Tokens y Variables
- [ ] Migrar colores HEX hardcodeados a tokens existentes
- [ ] Reemplazar valores de espaciado (padding/margin) por variables
- [ ] Actualizar valores de border-radius por tokens
- [ ] Migrar valores de font-size a escala tipográfica
- [ ] Reemplazar sombras (box-shadow) hardcodeadas por tokens

### Ajustes Visuales
- [ ] Cambiar valores de opacidad (hacer más/menos transparente)
- [ ] Ajustar valores de z-index dentro de rango conocido
- [ ] Modificar valores de media queries (breakpoints)
- [ ] Cambiar duraciones de transiciones/animaciones
- [ ] Ajustar valores de backdrop-filter

### Layout (Cambios Simples)
- [ ] Cambiar valor de gap en grids/flexboxes
- [ ] Ajustar max-width o min-width de contenedores
- [ ] Modificar valores de object-fit (cover, contain, etc.)

## ✅ Refactors Simples

### JavaScript/TypeScript
- [ ] Renombrar variables locales (no exportadas)
- [ ] Extraer expresiones complejas a funciones auxiliares
- [ ] Reordenar imports alfabéticamente
- [ ] Eliminar código comentado muerto
- [ ] Agregar tipos explícitos donde el inferido es any
- [ ] Convertir funciones a arrow functions (consistentemente)
- [ ] Agregar early returns para reducir anidación

### Vue Components
- [ ] Renombrar props internas (no expuestas al padre)
- [ ] Extraer computed properties duplicadas
- [ ] Mover lógica de template a methods/composables
- [ ] Agregar key attributes en v-for faltantes
- [ ] Renombrar emits internos

### Estructura
- [ ] Mover funciones utilitarias a archivos helpers
- [ ] Reorganizar imports agrupando por tipo
- [ ] Separar interfaces/types a archivos de tipos

## ✅ Configuración

### Archivos de Config
- [ ] Actualizar thresholds de cobertura de tests
- [ ] Modificar reglas de linting (desactivar/habilitar)
- [ ] Agregar exclusiones a .gitignore
- [ ] Actualizar versiones de dependencias (patch/minor)
- [ ] Modificar scripts de package.json
- [ ] Agregar variables de entorno de desarrollo

### CI/CD
- [ ] Modificar timeouts de workflows
- [ ] Agregar pasos de logging/debug
- [ ] Actualizar versiones de actions de GitHub

## ✅ Documentación

### Código
- [ ] Agregar JSDoc a funciones públicas
- [ ] Actualizar comentarios obsoletos
- [ ] Agregar ejemplos en comentarios
- [ ] Corregir typos en comentarios

### Archivos Markdown
- [ ] Actualizar README.md con información existente
- [ ] Corregir links rotos
- [ ] Agregar ejemplos de uso
- [ ] Actualizar tablas de contenido
- [ ] Corregir typos y gramática

### Diagramas
- [ ] Actualizar diagramas de arquitectura (si la estructura no cambió)
- [ ] Agregar notas aclaratorias

## ⚠️ Cambios que REQUIEREN VALIDACIÓN

Los siguientes pueden parecer seguros pero tienen riesgo oculto:

### CSS
- Cambiar selectores CSS (puede romper especificidad)
- Modificar position (static → absolute/fixed)
- Cambiar display (block → flex/grid)

### JavaScript
- Cambiar el orden de ejecución de funciones
- Modificar condicionales (agregar/eliminar checks)
- Cambiar valores por defecto de parámetros

### Vue
- Modificar lifecycles (created, mounted, etc.)
- Cambiar reactividad (ref vs reactive)
- Modificar watchers

## 🔴 NUNCA Ejecutar Automáticamente

- Cambios que afectan lógica de negocio
- Modificaciones en validaciones de datos
- Cambios en manejo de errores
- Modificaciones en seguridad (auth, CORS, etc.)
- Cambios en APIs públicas
- Modificaciones en base de datos (schemas, migrations)
- Cambios que requieren coordinación con otros equipos

## Pre-check Antes de Ejecutar Cambios Seguros

Antes de aplicar cualquier cambio "seguro":

1. [ ] Verificar que el archivo existe
2. [ ] Confirmar que hay tests que cubren el área (si aplica)
3. [ ] Ejecutar linter para verificar estado base
4. [ ] Hacer backup mental del rollback (git diff será suficiente)

## Post-check Después de Ejecutar

Después de aplicar cambios:

1. [ ] Ejecutar quality gate rápido (`npm run quality:fast` o equivalente)
2. [ ] Verificar que tests siguen pasando
3. [ ] Revisar visualmente el cambio (si es UI)
4. [ ] Actualizar docs/todo.md moviendo la tarea a done
