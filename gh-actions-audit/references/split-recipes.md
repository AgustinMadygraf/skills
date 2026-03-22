# Job Splitting Recipes

Common patterns for splitting jobs with rationale.

## Recipe: Lint/Test/Build Separation

**Before:** Single job running lint → test → build

**After:** Three parallel jobs after checkout

**Rationale:**
- Lint fails fast (syntax errors)
- Unit tests run in parallel with lint
- Build only happens if both pass
- Total wall time reduced

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: npm ci
    - run: npm run lint

test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: npm ci  
    - run: npm test

build:
  needs: [lint, test]
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: npm ci
    - run: npm run build
    - uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/
```

## Recipe: Heavy Step Isolation

**Before:** Job has one slow step blocking others

**After:** Isolate slow step with its own job

**Rationale:**
- Other jobs don't wait for slow step
- Can retry slow job independently
- Resource sizing per job type

```yaml
# Before: build-and-analyze job (20 min)
# After:
build:
  runs-on: ubuntu-latest
  steps:
    - run: npm run build

analyze:
  needs: build
  runs-on: ubuntu-latest-8-cores  # larger runner
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: dist
    - run: npm run analyze  # heavy operation
```

## Recipe: Fail-Fast vs Full-Matrix

**Before:** Matrix fails fast, missing other variants' results

**After:** Split required vs optional matrix runs

**Rationale:**
- Get all variant results even if one fails
- Required variants gate merge
- Optional variants inform but don't block

```yaml
# Required variants (gate merge)
test-required:
  strategy:
    matrix:
      node: [20]
      os: [ubuntu-latest]
  # ...

# Optional variants (informational)
test-optional:
  continue-on-error: true
  strategy:
    matrix:
      node: [18, 22]
      os: [windows-latest, macos-latest]
  # ...
```

## Recipe: Conditional Job Split

**Before:** Job has complex `if` conditions mixing concerns

**After:** Separate jobs with clear conditions

**Rationale:**
- Clearer when each job runs
- Different debug needs per path
- Easier to reason about

```yaml
# Instead of one job with complex ifs
test-pr:
  if: github.event_name == 'pull_request'
  # ...

test-schedule:
  if: github.event_name == 'schedule'
  # ... full suite

test-push:
  if: github.event_name == 'push'
  # ... smoke tests only
```
