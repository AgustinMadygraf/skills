# Reglas de Escalamiento a Decision Helper

Escalar a `decision-helper` cuando se cumpla al menos una condicion:

- Impacto cross-cutting en mas de 3 archivos o 2 capas.
- Cambio con riesgo de compatibilidad hacia atras.
- Trade-off de producto o arquitectura sin respuesta unica.
- Cambio de contrato publico de API.
- Introduccion de dependencia clave nueva.

No escalar cuando:

- El cambio es mecanico, reversible y de bajo riesgo.
- La decision esta cubierta por una regla explicita del skill.
- El impacto queda acotado y validable con tests simples.

Formato recomendado para escalar:

```md
## Duda de alto nivel
- Contexto:
- Opciones:
- Riesgos por opcion:
- Recomendacion inicial:
```
