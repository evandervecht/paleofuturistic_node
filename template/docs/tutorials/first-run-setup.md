# First-run setup

This tutorial takes you from a freshly generated project to running dev servers.

## Prerequisites

- Node.js at the version pinned in `.node-version` (or newer)
- pnpm — if missing, the bootstrap enables it via corepack

## 1. Bootstrap the environment

```sh
./workflow.cmd bootstrap
```

This initializes a git repository if needed, ensures pnpm is available, installs
all workspace dependencies, and (locally) offers to install the git hooks that
run the pre-commit checks and commit message linting.

The first `pnpm install` creates `pnpm-lock.yaml` — commit it; reproducible
installs and the container build depend on it.

## 2. Start the dev servers

```sh
./workflow.cmd develop
```

This starts the Fastify API on port 3000 and the Vite dev server for the web
app (which proxies `/api` requests to the API). Open the printed Vite URL and
you should see the scaffold page reporting the API status as `ok`.

## 3. Run the quality gates

```sh
./workflow.cmd format   # format code and organize imports
./workflow.cmd lint     # biome + type checks + commitlint
./workflow.cmd test     # vitest with coverage
```

You are ready to build. When you want to ship, continue with
[Make your first release](./make-your-first-release.md).
