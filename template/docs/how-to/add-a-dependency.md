# Add a dependency

Dependencies are managed per workspace package with pnpm.

## Runtime dependency of the API

```sh
pnpm --filter ./apps/api add <package>
```

## Runtime dependency of the web app

```sh
pnpm --filter ./apps/web add <package>
```

## Development tool used across the workspace

```sh
pnpm add -D -w <package>
```

## After adding

- Commit the updated `package.json` files **and** `pnpm-lock.yaml`.
- Run `./workflow.cmd secure` — new dependencies are audited and land in the SBOM.
- Run `./workflow.cmd quality` — knip flags dependencies that are declared but unused.
