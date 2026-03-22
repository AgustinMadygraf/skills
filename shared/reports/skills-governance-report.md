# Skills Governance Report

- Skills directories detected: 14
- Custom skills detected: 13
- AGENTS.md listed skills: 15
- Auto-fix applied: no changes needed

## Catalog
- Missing in AGENTS.md: none
- Stale AGENTS.md entries: none
- Broken file paths in AGENTS.md: 0

## Validation
- lint_skills.py: OK
  - Skill lint: OK
- quick_validate.py: 13/13 valid
  - clean-architecture-orchestrator: OK (Skill is valid!)
  - decision-helper: OK (Skill is valid!)
  - docs-maintainer: OK (Skill is valid!)
  - frontend-best-practices-audit: OK (Skill is valid!)
  - frontend-testing-vue-ts-tailwind: OK (Skill is valid!)
  - gh-actions-audit: OK (Skill is valid!)
  - skill-backend-code-audit: OK (Skill is valid!)
  - skill-backend-orchestrator: OK (Skill is valid!)
  - skill-backend-testing: OK (Skill is valid!)
  - skill-frontend-orchestrator: OK (Skill is valid!)
  - skills-governance-maintainer: OK (Skill is valid!)
  - testing-general: OK (Skill is valid!)
  - todo-workflow: OK (Skill is valid!)

## Overlap Risk
- testing-general <-> frontend-testing-vue-ts-tailwind
- testing-general <-> skill-backend-testing
- clean-architecture-orchestrator <-> frontend-best-practices-audit
- clean-architecture-orchestrator <-> skill-backend-code-audit

## Auto-fix Details
- No precedence updates were required.

## Recommended Actions
1. Resolve catalog mismatches first.
2. Keep lint + quick_validate green on every skill change.
3. Enforce specialized-over-generic precedence when overlap exists.
