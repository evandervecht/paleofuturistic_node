# Make your first release

Releases follow conventional commits: the version bump, changelog, tag, and
release branch are all derived from your commit history.

## 1. Check the tree

Make sure `main` is clean and in sync with origin:

```sh
./workflow.cmd release.validate
```

## 2. Preview the changelog

```sh
./workflow.cmd release.changelog
```

## 3. Cut the release

```sh
./workflow.cmd release -i minor
```

This creates a `release/<version>` branch, bumps the version in
`package.json`, writes the changelog, commits, tags `v<version>`, pushes the
branch and tag, and opens a release pull request when the host CLI (`gh` or
`glab`) is available.

Valid increments: `major`, `minor`, `patch`, `alpha`, `beta`, `rc`.

## 4. Merge and publish

Merging the release PR into `main` leaves the tag pointing at the released
snapshot. The publish pipeline (triggered by the `v*` tag) builds the container
image, pushes it to the registry, and uploads the SBOM where configured.
