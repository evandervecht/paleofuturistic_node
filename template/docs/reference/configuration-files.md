# Configuration files

| File | Purpose |
|------|---------|
| `package.json` | Workspace root: shared dev tooling, release configuration (`commit-and-tag-version` key) |
| `pnpm-workspace.yaml` | Declares the `apps/*` and `packages/*` workspace layout |
| `.node-version` | Node version pin, consumed by version managers and CI |
| `.npmrc` | pnpm settings (`engine-strict`) |
| `biome.json` | Formatting, linting, and import-organizing rules |
| `tsconfig.base.json` | Strict TypeScript defaults every package extends |
| `commitlint.config.mjs` | Conventional-commit message rules |
| `knip.json` | Unused files/exports/dependencies analysis |
| `typedoc.json` | API reference generation into `docs/reference/api` |
| `.security-overrides` | Allowlisted security advisories with optional expirations |
| `.githooks/` | Pre-commit and commit-msg hooks (activated by bootstrap) |
| `_CI/` | The workflow task runner (zero-dependency Node ESM) |
| `Dockerfile` | Multi-stage production image build |
