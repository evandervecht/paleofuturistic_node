/** Formatting task definitions. */

import { execute, logged, runSteps } from './shared.mjs';

/** Format code with biome. */
export const biomeFormat = logged('format.biome', () => {
  execute('pnpm exec biome format --write .');
});

/** Organize imports (biome assist). */
export const organizeImports = logged('format.imports', () => {
  execute('pnpm exec biome check --write --formatter-enabled=false --linter-enabled=false .');
});

/** Format code and organize imports; reports all failures before exiting. */
export const format = logged('format', async () => {
  await runSteps([biomeFormat, organizeImports]);
});

export const namespace = {
  name: 'format',
  defaultTask: 'all',
  tasks: {
    all: { fn: format, help: 'Format code and organize imports (biome)' },
    biome: { fn: biomeFormat, help: 'Format code with biome' },
    imports: { fn: organizeImports, help: 'Organize imports (biome assist)' },
  },
};
