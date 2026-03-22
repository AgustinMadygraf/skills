# Overlap Rules

## Priority Order

1. User-explicit skill name always wins.
2. Specialized skill wins over generic skill.
3. Orchestrator wins when the user asks for end-to-end processing.

## Canonical Precedence

- Frontend testing: `frontend-testing-vue-ts-tailwind` > `testing-general`
- Backend testing: `skill-backend-testing` > `testing-general`
- Frontend audit: `frontend-best-practices-audit` > `clean-architecture-orchestrator` for UI/Vue concerns
- Backend audit: `skill-backend-code-audit` > `clean-architecture-orchestrator` for FastAPI concerns
- Full backlog execution: `todo-workflow` only after tasks are curated

## Escalation

If two specialized skills still conflict, prefer the one that matches:
- Stack keywords explicitly present in request, then
- Directory scope (`src/frontend`, `src/backend`), then
- Most recent active workflow from docs/todo.md context.
