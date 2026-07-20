# Design principles and lineage

This template is a Node/React port of
[paleofuturistic_python](https://github.com/costastf/paleofuturistic_python),
which itself descends from
[Straight to the Money](https://github.com/Carlovo/straight_to_the_money).
The port preserves the architecture and trades only the language-specific
tooling.

## Preserved principles

- **One launcher, everywhere.** `workflow.cmd` is the same polyglot sh/cmd
  file; every task is `./workflow.cmd <namespace>.<task>` on every platform.
- **Portable CI tooling.** The Python template vendors Invoke so tasks run
  without global installs. Node needs no vendoring: the runner
  (`_CI/workflow.mjs`) is written against the standard library only, so it
  runs before `pnpm install` — which is what lets bootstrap be a task.
- **Bootstrap as a pre-task.** Every command runs the bootstrap first; the
  first thing a new contributor types just works.
- **Security is a gate, not a report.** The audit fails builds; allowlist
  entries carry expiration dates so exceptions cannot rot silently.
- **Releases are derived, not typed.** Conventional commits drive version,
  changelog, and tags; the release flow validates the tree and works through
  a reviewable release branch + PR.
- **The template tests itself.** Fast structural invariants run over every
  knob combination; the full QA cycle runs the generated project's own
  toolchain per matrix cell in CI.

## Deliberate divergences

- **The generated project is an application, not a library.** "Publish" means
  a container image rather than a package registry upload.
- **No dependency-cache container images in CI.** pnpm's store plus
  `actions/setup-node` caching covers what the Python template needed a
  custom deps image for.
- **Git hooks ship as plain scripts** (`.githooks/` + `core.hooksPath`)
  instead of the pre-commit framework, keeping the no-extra-tooling promise.
