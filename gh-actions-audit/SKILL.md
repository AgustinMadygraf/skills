---
name: gh-actions-audit
description: "Audit, diagnose, and fix GitHub Actions workflow failures. Supports failure analysis (audit:fail), preventive checks (audit:prevent), and job splitting with enhanced debugging. Automatically integrates with todo-workflow for task tracking. Use when GitHub Actions jobs fail, workflows need optimization, job splitting is considered for better parallelism/debugging, or preventive audit of workflow health is needed. Trigger with explicit invocation or when workflow failures are mentioned."
---


# GitHub Actions Audit Skill

Audit, diagnose and fix GitHub Actions workflows with automated analysis, job splitting, and enhanced debugging.

## Capabilities

- **Failure Analysis** (`audit:fail`): Diagnose root cause from job YAML + error logs
- **Preventive Audit** (`audit:prevent`): Static analysis of workflows before failure
- **Job Splitting**: Intelligently divide monolithic jobs for better parallelism
- **Debug Enhancement**: Add comprehensive logging and diagnostics
- **Todo Integration**: Auto-create and resolve tasks via `todo-workflow`

## Modes

### Mode: `audit:fail` (Failure Diagnosis)

Use when job has failed. Requires:
- Job YAML (or workflow name + job name)
- Error output (from `gh run view`, logs, or direct paste)

**Process:**
1. Parse job structure and dependencies
2. Analyze error patterns against known failures
3. Determine if fix is inline, requires job split, or new composite action
4. Generate fix code
5. If effort > 30 min, create `docs/todo.md` entry
6. Apply fix (auto if `--auto` flag, else ask)

### Mode: `audit:prevent` (Preventive Check)

Use proactively on workflow files.

**Checks:**
- Missing `timeout-minutes`
- Secrets in env without `required: false`
- Missing error handling (`if: failure()`)
- Debuggability gaps (no artifacts on fail)
- Split candidates (jobs > 15 min, sequential steps)

## Input Formats

Accepts job info in priority order:

1. **Full YAML + Logs** (best): Paste job definition + error output
2. **GitHub CLI JSON**: `gh run view --job=<id> --json`
3. **Workflow reference**: `workflow.yml:job-name` + error description

## Output Structure

Every audit produces:

```
📋 DIAGNOSIS
   Root cause classification
   Confidence level (high/medium/low)

🔧 RECOMMENDATION  
   Fix approach (inline / split / new-action)
   Risk assessment

📦 DELIVERABLES
   Generated files (if any)
   Diffs to apply

✅ NEXT STEPS
   Todo items created (if applicable)
   Verification commands
```

## Job Splitting Decision Matrix

| Condition | Split? | Rationale |
|-----------|--------|-----------|
| Job > 20 min | Yes | Parallelism benefit |
| Steps > 10 | Consider | Cognitive load, granularity |
| Mixed concerns (build+test+deploy) | Yes | Separation of phases |
| Shared state via files only | Yes | Artifact passing works |
| Complex env/state sharing | No | Cost > benefit |
| Matrix strategy applicable | Yes | Native parallelism |

## Debug Enhancement Patterns

Always add to jobs being split or fixed:

```yaml
# Step-level debug
timeout-minutes: <calculated-from-history>

# On failure diagnostics
- name: Debug / Context
  if: failure()
  run: |
    echo "::group::Environment"
    env | grep -E '^(GITHUB|RUNNER)' || true
    echo "::endgroup::"
    
    echo "::group::Disk usage"
    df -h
    du -sh . 2>/dev/null || true
    echo "::endgroup::"

# Artifact capture
- name: Upload debug artifacts
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: debug-${{ github.job }}-${{ github.run_id }}
    path: |
      *.log
      .tmp-*/
    retention-days: 7
```

## Composite Action Generation

When job split creates reusable logic:

1. Create `.github/actions/<action-name>/action.yml`
2. Extract common inputs/outputs
3. Add `debug` input flag (default: false)
4. Include diagnostic steps conditional on `debug` or `failure()`
5. Reference from both split jobs

## Integration with todo-workflow

Auto-create todo items when:
- Fix requires > 30 min of work
- Job split needs validation across multiple runs
- New composite action requires documentation
- Root cause is infrastructure/external dependency

Use `SetTodoList` tool with structured items:
```yaml
- title: "[GHA] Fix <job-name>: <short-cause>"
  status: pending
  # Body contains diagnosis + plan
```

Then invoke todo-workflow resolution.

## Autonomy Levels

Default: **Ask before modifying**

Override with context flag:
- `auto:fix` → Apply inline fixes without asking
- `auto:split` → Split jobs if criteria met
- `auto:all` → Full autonomy (use with caution)

## References

- Failure patterns: `references/failure-patterns.md`
- Job templates: `references/job-templates.md`
- Split recipes: `references/split-recipes.md`

## Scripts

- `scripts/analyze-failure.js`: Parse logs, classify errors
- `scripts/generate-split.js`: Generate split job YAML

Use scripts for deterministic operations. Read only when modifying.

