# Build and push a container

The `Dockerfile` builds the whole workspace and ships a pruned production
image in which the API serves the built web app as static assets.

## Build locally

```sh
./workflow.cmd container.build
```

This requires `pnpm-lock.yaml` to be committed (the image installs with
`--frozen-lockfile`) and tags the image with the current version and `latest`.

## Run it

```sh
docker run --rm -p 3000:3000 <project-slug>:latest
```

The web app is served on `/`, the API under `/api/`.

## Push to a registry

```sh
CONTAINER_REGISTRY=ghcr.io/<owner> ./workflow.cmd container.publish
```

The publish pipeline does the same automatically for every `v*` tag.
