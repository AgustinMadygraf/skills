# Job Templates for Split Scenarios

Templates for common job splitting patterns.

## Template: Build + Test Split

Original monolithic job does build then test. Split for faster feedback.

```yaml
# Job 1: Build
build:
  runs-on: ubuntu-latest
  timeout-minutes: 10
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - run: npm run build
    - uses: actions/upload-artifact@v4
      with:
        name: build-output
        path: dist/
        retention-days: 1

# Job 2: Test (parallel by type)
test-unit:
  needs: build
  runs-on: ubuntu-latest
  timeout-minutes: 10
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - uses: actions/download-artifact@v4
      with:
        name: build-output
        path: dist/
    - run: npm test
    - name: Debug on failure
      if: failure()
      run: |
        echo "::group::Test failures"
        find . -name "*.log" -exec cat {} \; || true
        echo "::endgroup::"

test-e2e:
  needs: build
  runs-on: ubuntu-latest
  timeout-minutes: 15
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - uses: actions/download-artifact@v4
      with:
        name: build-output
        path: dist/
    - run: npm run test:e2e
    - name: Upload E2E artifacts
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: e2e-debug
        path: test-results/
        retention-days: 7
```

## Template: Matrix Strategy Split

When job has platform/version variants.

```yaml
test-matrix:
  runs-on: ${{ matrix.os }}
  timeout-minutes: 15
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, windows-latest]
      node: [18, 20, 22]
      exclude:
        - os: windows-latest
          node: 18
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node }}
    - run: npm ci
    - run: npm test
      env:
        NODE_VERSION: ${{ matrix.node }}
    - name: Debug on failure
      if: failure()
      run: |
        echo "Failed on ${{ matrix.os }} with Node ${{ matrix.node }}"
```

## Template: Multi-Environment Deploy

Split deploy to dev/staging/prod with gates.

```yaml
deploy-dev:
  needs: test
  runs-on: ubuntu-latest
  environment: development
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: build-output
    - run: ./scripts/deploy.sh dev

deploy-staging:
  needs: deploy-dev
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: build-output
    - run: ./scripts/deploy.sh staging

deploy-prod:
  needs: deploy-staging
  runs-on: ubuntu-latest
  environment: production
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: build-output
    - run: ./scripts/deploy.sh prod
```

## Template: Debug-Enhanced Job

Wrapper adding debug capabilities to any job.

```yaml
example-job:
  runs-on: ubuntu-latest
  timeout-minutes: 15
  env:
    DEBUG_MODE: ${{ runner.debug || inputs.debug }}
  steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Pre-step diagnostics
      run: |
        echo "::group::Runner info"
        echo "OS: $RUNNER_OS"
        echo "Arch: $RUNNER_ARCH"
        echo "Debug: $DEBUG_MODE"
        echo "::endgroup::"

    # ... actual job steps ...

    - name: Post-failure diagnostics
      if: failure()
      run: |
        echo "::group::Environment variables"
        env | sort || true
        echo "::endgroup::"
        
        echo "::group::Process list"
        ps aux || true
        echo "::endgroup::"
        
        echo "::group::Disk usage"
        df -h
        du -sh . 2>/dev/null || true
        echo "::endgroup::"

    - name: Upload debug artifacts
      if: failure() || env.DEBUG_MODE == '1'
      uses: actions/upload-artifact@v4
      with:
        name: debug-${{ github.job }}-${{ github.run_attempt }}
        path: |
          *.log
          .tmp-*/
          coverage/
        retention-days: 7
```
