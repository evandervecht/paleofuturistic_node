# Paleofuturistic Node

[![Documentation: Diátaxis](https://img.shields.io/badge/docs-Di%C3%A1taxis-009485?logo=readthedocs&logoColor=white)](https://diataxis.fr/)

> _The Node/React development workflow your past self had always hoped for is finally here._

This is a [copier](https://copier.readthedocs.io/) template that generates a fully scaffolded, enterprise-ready **Node/React monorepo** — a pnpm workspace with a Fastify API, a Vite + React web app, and a shared types package; biome-formatted, vitest-tested, vitepress-documented, with a zero-dependency CI task runner, SBOM generation, and optional Dependency Track integration.

It is the Node/React sibling of [paleofuturistic_python](https://github.com/costastf/paleofuturistic_python) and mirrors its architecture: the same `workflow.cmd` launcher, the same task namespaces, the same copier knobs, and the same matrix-tested template QA.

## Contents

- [Using the template](#using-the-template)
  - [Setup](#setup)
  - [Workflow (in the generated project)](#workflow-in-the-generated-project)
  - [Features](#features)
  - [Template knobs](#template-knobs)
  - [Tooling mapping](#tooling-mapping)
- [Developing the template](#developing-the-template)
  - [Test entry points](#test-entry-points)

## Using the template

Prerequisites: [uv](https://docs.astral.sh/uv/) (to run copier) and [Node.js](https://nodejs.org/) ≥ 20 with pnpm (the bootstrap enables pnpm via corepack when missing).

### Setup

- Initialize with `uvx copier copy --trust <template-repo-url> <destination-dir>` and fill in your project details.
- Run `./workflow.cmd bootstrap` — it initializes git, installs dependencies, and offers to install the git hooks.
- Commit `pnpm-lock.yaml` after the first bootstrap; reproducible installs and the container build depend on it.

### Workflow (in the generated project)

All commands in generated projects are invoked via `./workflow.cmd <namespace>.<task>`:

| Command | Description |
|---------|-------------|
| `./workflow.cmd format` | Format code and organize imports (biome) |
| `./workflow.cmd lint` | Run all linters (biome, tsc strict type checks, commitlint) |
| `./workflow.cmd test` | Run all tests with coverage (vitest) |
| `./workflow.cmd build` | Run security checks and build all packages |
| `./workflow.cmd release -i <type>` | Bump version, tag, push, and open the release PR |
| `./workflow.cmd quality` | Run code quality analysis (knip) |
| `./workflow.cmd secure` | Run security audit and generate SBOM |
| `./workflow.cmd document` | Build and view documentation (typedoc + vitepress) |
| `./workflow.cmd container.build` | Build the production container image |
| `./workflow.cmd develop` | Start the API and web dev servers in parallel |
| `./workflow.cmd develop.pre-commit` | Run all pre-commit hooks on the codebase |
| `./workflow.cmd bootstrap --force` | Re-run the development environment setup |

### Features

- **Portable CI tooling** — a task runner written against the Node standard library only; it works before `pnpm install` has ever run, no global installs required
- **Cross-platform** — `workflow.cmd` launcher works on Unix/macOS (sh) and Windows (cmd.exe)
- **Security** — audit-ci vulnerability scanning with expiring allowlist entries, CycloneDX SBOM generation (cdxgen), optional OWASP Dependency Track upload
- **Quality** — biome linting/formatting (including cognitive complexity), strict tsc type checking per package, knip unused-code analysis
- **Release automation** — conventional-commit-driven version bump, changelog generation, release branch + PR flow, container publish
- **Container support** — multi-stage Dockerfile shipping a pruned production image in which the API serves the web build
- **Documentation** — Diátaxis-organized vitepress site with API reference generation via typedoc

### Template knobs

The copier questions expose these switches; defaults in **bold**.

| Knob | Choices | Effect |
|------|---------|--------|
| `git_hosting_service` | **`github`** \| `gitlab` | Selects the CI host scaffolding and the matching `_CI/tasks/<host>.mjs` submodule. |
| `license` | **`Apache-2.0`** \| `MIT` \| `BSD-3-Clause` \| `None` | Ships the matching `LICENSE` file (`None` ships none). |
| `integrate_dependency_track` | **`true`** \| `false` | Toggles the SBOM-upload code in `_CI/tasks/secure.mjs`. |
| `integrate_pages` | **`true`** \| `false` | Opts the Pages workflow and `document.deploy-github` task in (effective only when `git_hosting_service = github`). |
| `node_version` | `20` \| **`22`** \| `24` | Node major pinned in `.node-version`, `engines`, and the container images. |

### Tooling mapping

For readers coming from paleofuturistic_python:

| Concern | Python template | This template |
|---------|-----------------|---------------|
| Package/env manager | uv | pnpm (workspace) |
| Task runner | vendored Invoke | zero-dependency Node ESM runner (`_CI/workflow.mjs`) |
| Lint + format | ruff (+ pylint) | biome |
| Type checking | ty | tsc `--strict`, per package |
| Complexity | complexipy | biome `noExcessiveCognitiveComplexity` |
| Tests | pytest (+ tox matrix) | vitest (+ v8 coverage) |
| Dead code / quality | pyscn | knip |
| Vulnerability audit | pip-audit | audit-ci |
| SBOM | cyclonedx-bom | cdxgen |
| Commit/release | commitizen | commitlint + commit-and-tag-version |
| Docs | properdocs (mkdocs) | vitepress + typedoc |
| Publish target | PyPI wheel | container image (ghcr/registry) |

## Developing the template

The commands below run **from this repo**, not from a generated project. They require uv, Node ≥ 20, and pnpm.

### Test entry points

| Command | Scope |
|---------|-------|
| `./workflow.cmd test.invariants` | Fast pytest layer — generates each matrix cell once and asserts structural invariants (no inner toolchain). Best signal-per-second. |
| `./workflow.cmd test` | Generate the template with default context and run the full inner QA cycle (`format`, `lint`, `test`, `build`, `quality`, `document`). |
| `./workflow.cmd test.combo --git-hosting-service <github\|gitlab> [--no-integrate-dependency-track] [--no-integrate-pages]` | Same as `test`, but for one explicit matrix cell. Use to reproduce a single CI failure locally. |
| `./workflow.cmd test.matrix` | Run every cell of the cartesian product; per-cell logs land in `reports/matrix/`. Defaults to sequential — CI parallelizes by fanning out across runners instead. |

CI (`.github/workflows/template-matrix.yaml`) runs `test.invariants` plus a fanned-out `test.combo` per matrix cell on every push to `main` and every pull request.

To skip known CVEs during template testing:

```bash
TEMPLATE_SECURITY_OVERRIDE="GHSA-xxxx-xxxx-xxxx" ./workflow.cmd test
```
