/** Code quality task definitions. */

import { execute, logged } from './shared.mjs';

/** Find unused files, exports, and dependencies with knip. */
export const knip = logged('quality.knip', () => {
  execute('pnpm exec knip');
});

/** Run code quality analysis. */
export const quality = logged('quality', async () => {
  await knip();
});

export const namespace = {
  name: 'quality',
  defaultTask: 'all',
  tasks: {
    all: { fn: quality, help: 'Run code quality analysis (knip)' },
    knip: { fn: knip, help: 'Detect unused files, exports, and dependencies' },
  },
};
