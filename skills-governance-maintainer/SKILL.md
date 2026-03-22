---
name: skills-governance-maintainer
description: "Maintains governance quality for local Codex skills. Use when you need to synchronize AGENTS.md with installed skills, validate SKILL.md/agents metadata, run shared skill linting, detect trigger overlaps, and produce an actionable governance report."
---

# Skills Governance Maintainer

Run a full governance pass on `~/.codex/skills` and keep the catalog and validations consistent.

## Workflow

1. Discover installed skills and classify:
- System skills: `skills/.system/*`
- Custom skills: direct folders in `skills/` excluding `.system` and `shared`

2. Validate catalog consistency:
- Read `~/.codex/AGENTS.md`.
- Verify each listed `(file: .../SKILL.md)` path exists.
- Detect installed skills missing from `AGENTS.md`.
- Detect catalog entries pointing to non-existent skills.

3. Validate skill integrity:
- Run shared lint: `skills/shared/scripts/lint_skills.py`.
- Run formal validator: `skills/.system/skill-creator/scripts/quick_validate.py` over custom skills.

4. Detect trigger overlap risks:
- Flag generic-vs-specialized collisions, especially:
  - `testing-general` vs `frontend-testing-vue-ts-tailwind` and `skill-backend-testing`
  - `clean-architecture-orchestrator` vs `frontend-best-practices-audit` and `skill-backend-code-audit`

5. Produce report and recommended changes:
- Write a compact report to `skills/shared/reports/skills-governance-report.md`.
- Include priority levels, concrete file references, and next actions.

## Execution

Prefer using `scripts/run.py`:

```bash
python ~/.codex/skills/skills-governance-maintainer/scripts/run.py
```

If the user asks to apply changes:
- Update `AGENTS.md` entries.
- Fix governance config/lint rules when they diverge from current standards.
- Keep changes minimal and reversible.

## Output Contract

Always return:
- Current inventory summary.
- Validation summary (`lint_skills` + `quick_validate`).
- Catalog mismatch summary.
- Overlap-risk summary.
- Recommended prioritized action plan.

## References

Use `references/overlap-rules.md` to keep overlap decisions consistent.
