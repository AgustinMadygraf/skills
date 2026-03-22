#!/usr/bin/env node
/**
 * Generate split job YAML from monolithic job
 * Usage: node generate-split.js <workflow-file> <job-name> [split-point]
 */

const fs = require('fs');
const yaml = require('js-yaml');

function parseJob(workflowFile, jobName) {
  const content = fs.readFileSync(workflowFile, 'utf8');
  const workflow = yaml.load(content);
  return workflow.jobs[jobName];
}

function findSplitPoints(job) {
  const points = [];
  const steps = job.steps || [];
  
  // Natural boundaries
  const boundaries = [
    { name: 'setup', patterns: ['checkout', 'setup-node', 'setup-python'] },
    { name: 'install', patterns: ['npm ci', 'pip install', 'bundle install'] },
    { name: 'build', patterns: ['npm run build', 'make', 'compile'] },
    { name: 'test', patterns: ['npm test', 'pytest', 'jest'] },
    { name: 'deploy', patterns: ['deploy', 'upload', 'publish'] },
  ];
  
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const stepName = (step.name || '').toLowerCase();
    const stepRun = (step.run || '').toLowerCase();
    
    for (const boundary of boundaries) {
      if (boundary.patterns.some(p => stepName.includes(p) || stepRun.includes(p))) {
        points.push({ index: i, boundary: boundary.name, step });
      }
    }
  }
  
  return points;
}

function generateSplitJob(originalJob, splitAtIndex, jobName, suffix) {
  const steps = originalJob.steps || [];
  const setupSteps = steps.slice(0, splitAtIndex);
  const jobSteps = steps.slice(splitAtIndex);
  
  // For subsequent jobs, only include checkout and artifact download
  const minimalSetup = steps.filter(s => {
    const name = (s.name || '').toLowerCase();
    return name.includes('checkout') || name.includes('download-artifact');
  });
  
  const newJob = {
    ...originalJob,
    steps: suffix === '1' 
      ? [...setupSteps, ...jobSteps]
      : [...minimalSetup, ...jobSteps],
  };
  
  // Add artifact upload if first job produces output
  if (suffix === '1' && jobSteps.some(s => (s.run || '').includes('build'))) {
    newJob.steps.push({
      name: 'Upload artifacts',
      uses: 'actions/upload-artifact@v4',
      with: {
        name: `${jobName}-output`,
        path: 'dist/',
        'retention-days': 1,
      },
    });
  }
  
  // Add debug steps
  newJob.steps.push({
    name: 'Debug on failure',
    if: 'failure()',
    run: `echo "Job ${jobName}-${suffix} failed"
env | grep -E '^(GITHUB|RUNNER)' || true`,
  });
  
  return newJob;
}

function main() {
  const [workflowFile, jobName, splitPoint] = process.argv.slice(2);
  
  if (!workflowFile || !jobName) {
    console.error('Usage: node generate-split.js <workflow-file> <job-name> [split-point]');
    process.exit(1);
  }
  
  const job = parseJob(workflowFile, jobName);
  const points = findSplitPoints(job);
  
  console.log('Detected split points:');
  points.forEach((p, i) => {
    console.log(`  ${i}: ${p.boundary} at step ${p.index} (${p.step.name || 'unnamed'})`);
  });
  
  if (splitPoint !== undefined) {
    const idx = parseInt(splitPoint);
    const point = points.find(p => p.index >= idx) || points[Math.floor(points.length / 2)];
    
    const job1 = generateSplitJob(job, point.index, jobName, '1');
    const job2 = generateSplitJob(job, point.index, jobName, '2');
    
    // Add dependency
    job2.needs = job2.needs || [];
    if (!Array.isArray(job2.needs)) job2.needs = [job2.needs];
    job2.needs.push(`${jobName}-1`);
    
    console.log('\n--- Generated Jobs ---\n');
    console.log(yaml.dump({
      [`${jobName}-1`]: job1,
      [`${jobName}-2`]: job2,
    }));
  }
}

if (require.main === module) {
  main();
}

module.exports = { parseJob, findSplitPoints, generateSplitJob };
