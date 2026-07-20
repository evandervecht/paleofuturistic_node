/** Linting task definitions. */

import { capture, execute, logged, runSteps } from './shared.mjs';

/** Run biome in CI mode: lint rules, format check, and assist check in one pass. */
export const biome = logged('lint.biome', () => {
  execute('pnpm exec biome ci .');
});

/** Report code that is not correctly formatted, without modifying any files. */
export const formatCheck = logged('lint.format-check', () => {
  execute('pnpm exec biome format .');
});

/** Type-check every workspace package with tsc. */
export const types = logged('lint.types', () => {
  execute('pnpm --recursive run typecheck');
});

/**
 * Lint commit messages against conventional commits.
 *
 * With --commit-msg-file (used by the commit-msg hook) checks that file;
 * otherwise checks the last committed message.
 */
export const commitlint = logged('lint.commitlint', (options = {}) => {
  if (options.commitMsgFile) {
    execute(`pnpm exec commitlint --edit "${options.commitMsgFile}"`);
  } else if (capture('git rev-parse HEAD').ok) {
    execute('pnpm exec commitlint --last --verbose');
  } else {
    console.log('No commits yet — skipping commitlint check.');
  }
});

/** Run all linting steps; reports all failures before exiting. */
export const lint = logged('lint', async (options = {}) => {
  await runSteps([biome, types, commitlint], options);
});

export const namespace = {
  name: 'lint',
  defaultTask: 'all',
  tasks: {
    all: { fn: lint, help: 'Run all linters (biome, tsc, commitlint)' },
    biome: { fn: biome, help: 'Run biome lint + format + assist checks' },
    'format-check': { fn: formatCheck, help: 'Check formatting without writing' },
    types: { fn: types, help: 'Type-check all workspace packages' },
    commitlint: { fn: commitlint, help: 'Lint commit messages (conventional commits)' },
  },
};
