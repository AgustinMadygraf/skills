# Formato Estandar de Hallazgos

Usar este formato en `docs/todo.md` para auditorias y testing:

```md
### [SEVERIDAD] Titulo corto del hallazgo
- Skill origen: `<skill-name>`
- Ubicacion: `<ruta/archivo[:linea]>`
- Riesgo: `<que puede salir mal>`
- Impacto: `<impacto tecnico/negocio>`
- Evidencia: `<dato observado>`
- Recomendacion: `<accion concreta>`
- Criterio de aceptacion: `<como verificar que quedo resuelto>`
```

Severidades validas: `critica`, `alta`, `media`, `baja`.
