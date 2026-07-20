/** Testing task definitions. */

import { execute, logged } from './shared.mjs';

/** Run the API test suite. */
export const api = logged('test.api', () => {
  execute('pnpm --filter ./apps/api run test');
});

/** Run the web test suite. */
export const web = logged('test.web', () => {
  execute('pnpm --filter ./apps/web run test');
});

/** Run all test suites across the workspace. */
export const test = logged('test', () => {
  execute('pnpm --recursive run test');
});

export const namespace = {
  name: 'test',
  defaultTask: 'all',
  tasks: {
    all: { fn: test, help: 'Run all tests (vitest, with coverage)' },
    api: { fn: api, help: 'Run the API test suite' },
    web: { fn: web, help: 'Run the web test suite' },
  },
};
