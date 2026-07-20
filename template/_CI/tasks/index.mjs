/** CI task registry for the project workflow. */

import * as bootstrap from './bootstrap.mjs';
import * as build from './build.mjs';
import * as container from './container.mjs';
import * as develop from './develop.mjs';
import * as document from './document.mjs';
import * as format from './format.mjs';
import * as lint from './lint.mjs';
import * as quality from './quality.mjs';
import * as release from './release.mjs';
import * as secure from './secure.mjs';
import * as test from './test.mjs';

export const namespaces = [
  bootstrap.namespace,
  build.namespace,
  container.namespace,
  develop.namespace,
  document.namespace,
  format.namespace,
  lint.namespace,
  quality.namespace,
  release.namespace,
  secure.namespace,
  test.namespace,
];
