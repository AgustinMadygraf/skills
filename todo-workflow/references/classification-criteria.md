# Criterios de Clasificación de Tareas

Guía detallada para clasificar tareas de `docs/todo.md` en certezas, dudas de bajo nivel y dudas de alto nivel.

## Certezas

### Definición
Tareas donde se tiene claro QUÉ hacer, DÓNDE hacerlo y CÓMO hacerlo. El riesgo es bajo y el scope está bien definido.

### Checklist de Certeza

- [ ] Archivo objetivo identificado y existe
- [ ] Cambio es mecánico (no requiere diseño)
- [ ] Patrón similar ya existe en el codebase
- [ ] Tests existentes cubren el área (o no aplica)
- [ ] No modifica APIs públicas
- [ ] No afecta lógica de negocio
- [ ] Es reversible fácilmente

### Ejemplos

| Tarea | ¿Certeza? | Justificación |
|-------|-----------|---------------|
| "Migrar color #ff8c00 a token" | ✅ Sí | Cambio mecánico, reemplazo directo |
| "Ajustar padding de 1rem a 1.5rem" | ✅ Sí | Cambio de valor, scope claro |
| "Renombrar función interna" | ✅ Sí | Refactor local, no expone API |
| "Agregar propiedad CSS faltante" | ✅ Sí | Completar implementación existente |

## Dudas de Bajo Nivel

### Definición
Tareas donde hay múltiples opciones técnicas válidas, el impacto es localizado y se pueden evaluar Pros/Contras objetivamente.

### Indicadores

- Opciones son mutuamente excluyentes pero igualmente válidas
- Impacto limitado a componente/módulo específico
- Se puede crear tabla de comparación objetiva
- No hay implicancias de arquitectura
- La decisión es reversible con costo medio

### Checklist de Evaluación

```markdown
### Opción A
- **Pros**: [lista]
- **Contras**: [lista]
- **Riesgo**: [Bajo/Medio/Alto]
- **Esforzo**: [Alto/Medio/Bajo]

### Opción B
- **Pros**: [lista]
- **Contras**: [lista]
- **Riesgo**: [Bajo/Medio/Alto]
- **Esforzo**: [Alto/Medio/Bajo]
```

### Ejemplos

| Tarea | Opciones a evaluar |
|-------|-------------------|
| "Mejorar layout del formulario" | Flexbox vs Grid vs CSS Tables |
| "Agregar validación" | Validación síncrona vs asíncrona |
| "Manejar estado" | useState vs useReducer vs Context |
| "Implementar animación" | CSS transitions vs Framer Motion |

## Dudas de Alto Nivel

### Definición
Tareas que involucran decisiones arquitectónicas, de producto o estratégicas con impacto cross-cutting.

### Indicadores

- Impacta múltiples capas del sistema (domain, application, infrastructure, UI)
- Afecta contratos de API o interfaces públicas
- Cambia la estrategia de testing o deployment
- Involucra decisiones de negocio o UX significativas
- Tiene costo de rollback alto
- Afecta a otros equipos o sistemas

### Categorías de Dudas Alto Nivel

#### 1. Arquitectura
- Migraciones tecnológicas (ej: cambiar de framework)
- Cambios en patrones de diseño
- Modificaciones en límites de capas
- Decisiones sobre estado global vs local

#### 2. Producto
- Cambios en flujos de usuario principales
- Nuevas funcionalidades core
- Modificaciones en modelo de datos de negocio
- Decisiones de alcance y priorización

#### 3. Estrategia
- Cambios en políticas de calidad
- Modificaciones en procesos de CI/CD
- Decisiones sobre deuda técnica vs features
- Estrategias de testing (unitario vs E2E vs ambos)

### Proceso de Escalamiento

1. **Identificar** la categoría (arquitectura/producto/estrategia)
2. **Documentar** en `docs/decision/questions.md`:
   - Contexto completo
   - Stakeholders afectados
   - Opciones consideradas con trade-offs
   - Implicancias a corto y largo plazo
3. **Consultar** al usuario con la información estructurada
4. **Registrar decisión** como ADR una vez resuelta

## Casos Borde

### ¿Certeza o Duda Bajo Nivel?

**Situación**: "Refactorizar componente X"

**Clasificación**: Depende
- Si es extracción de función utilitaria → Certeza
- Si es reestructuración del componente → Duda Bajo Nivel
- Si implica cambiar la API del componente → Duda Alto Nivel

### ¿Duda Bajo o Alto Nivel?

**Situación**: "Agregar nuevo feature de autenticación"

**Clasificación**: Generalmente Duda Alto Nivel
- Afecta múltiples capas (UI, application, infrastructure)
- Impacta seguridad
- Requiere decisión de producto sobre flujo UX

**Pero podría ser Duda Bajo Nivel si**:
- La arquitectura de auth ya está definida
- Solo se implementa un nuevo método (ej: OAuth provider adicional)
- No cambia el flujo existente

## Regla de Oro

> Cuando en duda, asumir el nivel superior. Mejor consultar de más que ejecutar de menos.

- Si no estás 100% seguro de que sea Certeza → tratar como Duda Bajo Nivel
- Si hay ambigüedad en el scope → tratar como Duda Alto Nivel
