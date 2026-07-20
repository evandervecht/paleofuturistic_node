import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/server.ts'],
  format: ['esm'],
  target: 'node20',
  clean: true,
  sourcemap: true,
  // Bundle the internal workspace package so the built output has no
  // workspace-protocol dependencies at runtime.
  noExternal: [/^@[^/]+\/shared$/],
});
