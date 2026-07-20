/** Development helper task definitions. */

import { execute, logged, runSteps } from './shared.mjs';

/** The checks the pre-commit hook runs: biome (lint + format + assist) and type-checking. */
export const preCommit = logged('develop.pre-commit', async () => {
  await runSteps([
    logged('develop.biome', () => execute('pnpm exec biome check .')),
    logged('develop.types', () => execute('pnpm --recursive run typecheck')),
  ]);
});

/** Start the API and web dev servers in parallel. */
export const dev = logged('develop.dev', () => {
  execute('pnpm --recursive --parallel run dev');
});

export const namespace = {
  name: 'develop',
  defaultTask: 'dev',
  tasks: {
    dev: { fn: dev, help: 'Start API and web dev servers in parallel' },
    'pre-commit': { fn: preCommit, help: 'Run all pre-commit checks on the codebase' },
  },
};
