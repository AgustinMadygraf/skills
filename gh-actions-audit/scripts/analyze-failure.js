#!/usr/bin/env node
/**
 * Analyze GitHub Actions failure from JSON log output
 * Usage: node analyze-failure.js <job-json-file>
 */

const fs = require('fs');

// Failure pattern definitions
const PATTERNS = {
  timeout: {
    regex: /exceeded the maximum execution time|timeout|timed out/i,
    category: 'timeout',
    severity: 'high',
  },
  permission: {
    regex: /permission denied|403|unauthorized|forbidden/i,
    category: 'permission',
    severity: 'high',
  },
  dependency: {
    regex: /npm ERR|pip install|apt-get|404 not found|unable to resolve/i,
    category: 'dependency',
    severity: 'medium',
  },
  resource: {
    regex: /no space left|out of memory|exit code 137|killed/i,
    category: 'resource',
    severity: 'high',
  },
  test: {
    regex: /test failed|assertion failed|expect.*received/i,
    category: 'test',
    severity: 'medium',
  },
  secret: {
    regex: /secret.*not found|input required|bad substitution/i,
    category: 'secret',
    severity: 'high',
  },
  action: {
    regex: /unable to resolve action|deprecated|node version/i,
    category: 'action',
    severity: 'low',
  },
};

function analyzeLog(logContent) {
  const findings = [];
  
  for (const [name, pattern] of Object.entries(PATTERNS)) {
    if (pattern.regex.test(logContent)) {
      findings.push({
        pattern: name,
        category: pattern.category,
        severity: pattern.severity,
        matches: logContent.match(pattern.regex).slice(0, 3),
      });
    }
  }
  
  return findings;
}

function suggestFix(findings, jobYaml) {
  const fixes = [];
  
  for (const finding of findings) {
    switch (finding.category) {
      case 'timeout':
        fixes.push({
          type: 'config',
          action: 'increase timeout-minutes or split job',
          yaml: 'timeout-minutes: 30  # adjust based on history',
        });
        break;
      case 'resource':
        fixes.push({
          type: 'optimization',
          action: 'add cleanup steps, use larger runner, or split job',
          yaml: `- run: |
    docker system prune -f || true
    rm -rf node_modules/.cache || true`,
        });
        break;
      case 'test':
        fixes.push({
          type: 'retry',
          action: 'add retry logic for flaky tests',
          yaml: `- run: |
    for i in 1 2 3; do
      npm test && break || sleep 5
    done`,
        });
        break;
      case 'permission':
        fixes.push({
          type: 'permission',
          action: 'check GITHUB_TOKEN permissions or secrets',
          yaml: `permissions:
  contents: read
  packages: write`,
        });
        break;
    }
  }
  
  return fixes;
}

function main() {
  const inputFile = process.argv[2];
  
  if (!inputFile) {
    console.error('Usage: node analyze-failure.js <log-file>');
    process.exit(1);
  }
  
  const content = fs.readFileSync(inputFile, 'utf8');
  const findings = analyzeLog(content);
  const fixes = suggestFix(findings, '');
  
  console.log(JSON.stringify({
    findings,
    fixes,
    splitRecommended: findings.some(f => ['timeout', 'resource'].includes(f.category)),
  }, null, 2));
}

if (require.main === module) {
  main();
}

module.exports = { analyzeLog, suggestFix, PATTERNS };
