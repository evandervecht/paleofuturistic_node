/** Bootstrap task definitions for initial development environment setup. */

import { closeSync, existsSync, openSync } from 'node:fs';
import process from 'node:process';
import readline from 'node:readline/promises';
import { SENTINEL } from './configuration.mjs';
import { capture, ExitError, execute, isCi, logged, which } from './shared.mjs';

function ensureGitRepo() {
  if (!capture('git rev-parse --git-dir').ok) {
    execute('git init');
  }
}

function ensurePnpm() {
  if (which('pnpm')) {
    return;
  }
  if (which('corepack')) {
    console.log('pnpm not found — enabling it via corepack.');
    execute('corepack enable pnpm');
    return;
  }
  console.error('pnpm not found. Install it via corepack or https://pnpm.io/installation.');
  throw new ExitError(1);
}

function installDependencies() {
  execute('pnpm install');
}

function installGitHooks() {
  ensureGitRepo();
  execute('git config core.hooksPath .githooks');
}

/**
 * Bootstrap steps with CI-aware execution behavior. Steps with a prompt ask
 * locally and are skipped in non-interactive contexts unless ciBehavior is
 * 'run'. Register new ones here as needed.
 */
const STEPS = [
  { name: 'git repository', action: ensureGitRepo, prompt: '', ciBehavior: 'run' },
  { name: 'pnpm availability', action: ensurePnpm, prompt: '', ciBehavior: 'run' },
  { name: 'dependency install', action: installDependencies, prompt: '', ciBehavior: 'run' },
  { name: 'git hooks', action: installGitHooks, prompt: 'Install git hooks? [y/N] ', ciBehavior: 'skip' },
];

async function runBootstrapSteps() {
  const nonInteractive = isCi() || !process.stdin.isTTY;
  for (const step of STEPS) {
    if (!step.prompt) {
      step.action();
    } else if (nonInteractive) {
      if (step.ciBehavior === 'run') {
        console.log(`  Running ${step.name}...`);
        step.action();
      } else {
        console.log(`  Skipping ${step.name} (non-interactive mode)`);
      }
    } else {
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      const answer = (await rl.question(step.prompt)).trim().toLowerCase();
      rl.close();
      if (answer === 'y' || answer === 'yes') {
        step.action();
      }
    }
  }
}

/** Set up the development environment (runs once; --force to re-run). */
export const bootstrap = logged('bootstrap', async (options = {}) => {
  if (existsSync(SENTINEL) && existsSync('node_modules') && !options.force) {
    return;
  }
  await runBootstrapSteps();
  closeSync(openSync(SENTINEL, 'w'));
});

export const namespace = {
  name: 'bootstrap',
  defaultTask: 'all',
  tasks: {
    all: { fn: bootstrap, help: 'Set up the development environment (once; --force to re-run)' },
  },
};
