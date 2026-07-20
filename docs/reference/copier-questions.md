# Copier questions

| Question | Type | Default | Effect |
|----------|------|---------|--------|
| `project_name` | str | `Paleofuturistic Node Project` | Display name used in the README, docs, and web app |
| `project_slug` | str | slugified project name | npm-safe name; also the workspace scope (`@<slug>/api`, `@<slug>/web`, `@<slug>/shared`) and container image name |
| `project_description` | str | — | Short description used in package metadata and docs |
| `full_name` | str | — | Author name in `package.json` and the LICENSE |
| `email` | str | — | Author email in `package.json` |
| `node_version` | choice | `22` | Node major pinned in `.node-version`, `engines`, and container images |
| `license` | choice | `Apache-2.0` | Ships the matching LICENSE (`None` ships none and drops the `license` field) |
| `git_hosting_service` | choice | `github` | Ships `.github/workflows/` or `.gitlab-ci.yml`, plus the matching `_CI/tasks/<host>.mjs` |
| `integrate_dependency_track` | bool | `true` | Adds `secure.sbom-upload` and the Dependency Track wiring |
| `integrate_pages` | bool | `true` | Adds the Pages workflow and `document.deploy-github` (github only) |
