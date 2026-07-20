# Triage a security finding

`./workflow.cmd secure.audit` runs [audit-ci](https://github.com/IBM/audit-ci)
over the pnpm lockfile and fails on advisories of moderate severity or higher.

## 1. Understand the finding

The audit output names the advisory (usually a `GHSA-…` id), the affected
package, and the dependency path. Check whether your code exercises the
vulnerable behaviour.

## 2. Prefer fixing

- Upgrade the direct dependency that pulls the vulnerable package in.
- If the fix is in a transitive dependency, add a
  [pnpm override](https://pnpm.io/package_json#pnpmoverrides) to force the
  patched version.

## 3. Allowlist as a last resort

When no fix exists yet, add the advisory id to `.security-overrides`,
one entry per line, optionally with an expiration date:

```text
GHSA-xxxx-xxxx-xxxx::2026-12-31  # transitive in vitest, fix pending upstream
```

Expired entries are dropped automatically, so the audit starts failing again
once the deadline passes — overrides cannot rot silently.

For one-off runs, the same syntax works via the environment variable named
`<PROJECT>_SECURITY_OVERRIDE` (the project slug upper-cased, `-` → `_`).
