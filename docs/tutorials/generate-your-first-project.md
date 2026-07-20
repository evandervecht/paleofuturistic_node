# Generate your first project

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — runs copier without a global install
- Node.js ≥ 20 (pnpm is enabled via corepack by the project bootstrap)

## Generate

```sh
uvx copier copy --trust <template-repo-url> my-project
```

Answer the questions (project name, author, Node version, license, git host,
integrations). Copier renders the project, installs the chosen license, and
marks `workflow.cmd` executable.

## Bootstrap and verify

```sh
cd my-project
./workflow.cmd bootstrap
./workflow.cmd lint
./workflow.cmd test
```

The bootstrap initializes git, installs the pnpm workspace, and offers to
install the git hooks. Commit everything, including `pnpm-lock.yaml`:

```sh
git add -A
git commit -m "feat: initial project from template"
```

From here, continue with the generated project's own docs:
`docs/tutorials/first-run-setup.md` inside your new project.
