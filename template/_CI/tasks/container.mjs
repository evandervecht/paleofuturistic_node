/** Container task definitions. */

import process from 'node:process';
import { IMAGE_NAME } from './configuration.mjs';
import { containerEngine, ExitError, execute, logged, readRootPackage } from './shared.mjs';

/** Build the application container image, tagged with the current version and latest. */
export const build = logged('container.build', () => {
  const engine = containerEngine();
  const version = readRootPackage().version;
  execute(`${engine} build -t ${IMAGE_NAME}:${version} -t ${IMAGE_NAME}:latest .`);
});

/**
 * Push the container image to the registry named by CONTAINER_REGISTRY
 * (e.g. `ghcr.io/my-org`). Builds the image first.
 */
export const publish = logged('container.publish', () => {
  const registry = (process.env.CONTAINER_REGISTRY ?? '').replace(/\/$/, '');
  if (!registry) {
    console.error('CONTAINER_REGISTRY is not set (e.g. ghcr.io/my-org). Cannot publish the image.');
    throw new ExitError(1);
  }
  const engine = containerEngine();
  const version = readRootPackage().version;
  execute(`${engine} build -t ${IMAGE_NAME}:${version} -t ${IMAGE_NAME}:latest .`);
  for (const tag of [version, 'latest']) {
    execute(`${engine} tag ${IMAGE_NAME}:${tag} ${registry}/${IMAGE_NAME}:${tag}`);
    execute(`${engine} push ${registry}/${IMAGE_NAME}:${tag}`);
  }
});

export const namespace = {
  name: 'container',
  defaultTask: 'build',
  tasks: {
    build: { fn: build, help: 'Build the application container image' },
    publish: { fn: publish, help: 'Build and push the image to $CONTAINER_REGISTRY' },
  },
};
