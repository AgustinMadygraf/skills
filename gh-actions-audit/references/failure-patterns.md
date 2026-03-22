# GitHub Actions Failure Patterns

Reference for common failure patterns and their solutions.

## Timeout Failures

### Pattern: `The job running on runner ... has exceeded the maximum execution time of X minutes`

**Diagnosis:**
- Check `timeout-minutes` value
- Review step durations in log
- Identify hanging step (no output for >5 min)

**Solutions:**
1. Increase `timeout-minutes` if legitimate long-running
2. Add step-level timeouts
3. Split job at slow step boundary
4. Add `timeout` wrapper to commands

```yaml
# Step-level timeout
timeout-minutes: 10
```

## Dependency/Installation Failures

### Pattern: `npm ERR!`, `pip install failed`, `apt-get failed`

**Diagnosis:**
- Network connectivity (intermittent?)
- Registry availability
- Lock file out of sync
- Cache corruption

**Solutions:**
```yaml
# Retry wrapper
- run: |
    for i in 1 2 3; do
      npm ci && break || sleep 15
    done

# Cache validation
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: '**/package-lock.json'
```

## Permission Failures

### Pattern: `Permission denied`, `403 Forbidden`, `Unauthorized`

**Diagnosis:**
- `GITHUB_TOKEN` permissions
- Secrets availability
- Environment protection rules
- Fork vs branch execution

**Solutions:**
```yaml
permissions:
  contents: read
  packages: write
```

## Resource Exhaustion

### Pattern: `No space left on device`, `out of memory`, `exit code 137`

**Diagnosis:**
- Disk usage in debug output
- Memory-intensive steps
- Large artifact accumulation

**Solutions:**
```yaml
# Cleanup between steps
- run: |
    docker system prune -f || true
    rm -rf node_modules/.cache || true
```

## Flaky Test Failures

### Pattern: Tests pass/fail inconsistently

**Diagnosis:**
- Race conditions
- External dependencies
- Timing issues
- State pollution

**Solutions:**
1. Add retry logic
2. Isolate test state
3. Mock external calls
4. Split E2E from unit tests

## Secret/Variable Failures

### Pattern: `Input required and not supplied`, `bad substitution`

**Diagnosis:**
- Secret not defined in environment
- Var syntax error
- Missing `required: false` with fallback

**Solutions:**
```yaml
env:
  OPTIONAL_VAR: ${{ vars.OPTIONAL_VAR || 'default' }}
```

## Action/Version Failures

### Pattern: `Unable to resolve action`, `deprecated`, `node version`

**Diagnosis:**
- Action version deleted/archived
- Node version mismatch
- Breaking changes in major version

**Solutions:**
- Pin to SHA instead of tag
- Update to supported Node version
- Test action upgrade in isolated PR
