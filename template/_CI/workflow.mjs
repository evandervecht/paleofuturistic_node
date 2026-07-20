#!/usr/bin/env node
/**
 * Workflow dispatcher — the zero-dependency equivalent of the vendored Invoke
 * runner in paleofuturistic_python. Runs before `pnpm install`, so it must not
 * import anything outside the Node standard library.
 *
 * Usage: ./workflow.cmd <namespace>[.<task>] [options]
 * Examples:
 *   ./workflow.cmd lint
 *   ./workflow.cmd release -i minor
 *   ./workflow.cmd bootstrap --force
 */

import process from 'node:process';
import { namespaces } from './tasks/index.mjs';
import { ExitError } from './tasks/shared.mjs';

const FLAG_ALIASES = { i: 'increment', f: 'force' };
const BOOLEAN_FLAGS = new Set(['force', 'write', 'no-push', 'fix', 'verbose']);

function camelize(name) {
  return name.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
}

function parseFlag(argv, index) {
  const token = argv[index];
  if (!token.startsWith('-')) {
    console.error(`Unexpected argument: ${token}`);
    throw new ExitError(1);
  }
  let name = token.replace(/^--?/, '');
  let value;
  const equals = name.indexOf('=');
  if (equals !== -1) {
    value = name.slice(equals + 1);
    name = name.slice(0, equals);
  }
  name = FLAG_ALIASES[name] ?? name;
  if (value !== undefined) {
    return { name, value, consumed: 1 };
  }
  const next = argv[index + 1];
  if (!BOOLEAN_FLAGS.has(name) && next !== undefined && !next.startsWith('-')) {
    return { name, value: next, consumed: 2 };
  }
  return { name, value: true, consumed: 1 };
}

function parseOptions(argv) {
  const options = {};
  let index = 0;
  while (index < argv.length) {
    const { name, value, consumed } = parseFlag(argv, index);
    options[camelize(name)] = value;
    index += consumed;
  }
  return options;
}

function printUsage() {
  console.log('Usage: ./workflow.cmd <namespace>[.<task>] [options]\n');
  console.log('Available tasks:');
  for (const namespace of namespaces) {
    for (const [taskName, task] of Object.entries(namespace.tasks)) {
      const label = taskName === namespace.defaultTask ? namespace.name : `${namespace.name}.${taskName}`;
      console.log(`  ${label.padEnd(28)} ${task.help ?? ''}`);
    }
  }
}

function resolveTask(spec) {
  const [namespaceName, taskName] = spec.split('.', 2);
  const namespace = namespaces.find((candidate) => candidate.name === namespaceName);
  if (!namespace) {
    console.error(`Unknown namespace: ${namespaceName}\n`);
    printUsage();
    throw new ExitError(1);
  }
  const resolved = taskName ?? namespace.defaultTask;
  const task = namespace.tasks[resolved];
  if (!task) {
    console.error(`Unknown task: ${spec}\n`);
    printUsage();
    throw new ExitError(1);
  }
  return { namespace, task };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv[0] === '--list' || argv[0] === 'help') {
    printUsage();
    return;
  }
  const spec = argv[0];
  const options = parseOptions(argv.slice(1));
  const { namespace, task } = resolveTask(spec);
  if (namespace.name !== 'bootstrap') {
    const bootstrap = namespaces.find((candidate) => candidate.name === 'bootstrap');
    await bootstrap.tasks[bootstrap.defaultTask].fn({});
  }
  await task.fn(options);
}

try {
  await main();
} catch (error) {
  if (error instanceof ExitError) {
    process.exitCode = error.code;
  } else {
    console.error(error);
    process.exitCode = 1;
  }
}
