/** Build task definitions. */

import { audit, sbom } from './secure.mjs';
import { execute, logged } from './shared.mjs';

/** Build every workspace package (topological order). */
export const packages = logged('build.packages', () => {
  execute('pnpm --recursive run build');
});

/** Run security checks, generate the SBOM, and build all packages. */
export const build = logged('build', async () => {
  await audit();
  await sbom();
  await packages();
});

export const namespace = {
  name: 'build',
  defaultTask: 'all',
  tasks: {
    all: { fn: build, help: 'Run security checks and build all packages' },
    packages: { fn: packages, help: 'Build all workspace packages without security checks' },
  },
};
