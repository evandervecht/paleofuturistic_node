/** Shared utilities for CI task definitions. */

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import process from 'node:process';

/** Raised by tasks to signal failure; carries the process exit code. */
export class ExitError extends Error {
  constructor(code = 1) {
    super(`Task failed with exit code ${code}`);
    this.code = code;
  }
}

const OPEN_COMMAND = {
  linux: 'xdg-open',
  macos: 'open',
  windows: 'start',
  wsl: 'wslview', // from the wslu package; falls back to xdg-open if not installed
};

/** Detect CI environment (GitHub Actions, GitLab CI, etc.). */
export function isCi() {
  return (process.env.CI ?? '').toLowerCase() === 'true';
}

/** Return the current operating system ('windows', 'macos', 'linux', or 'wsl'). */
export function getOperatingSystem() {
  if (process.platform === 'win32') {
    return 'windows';
  }
  if (process.platform === 'darwin') {
    return 'macos';
  }
  if (process.platform === 'linux') {
    try {
      const version = readFileSync('/proc/version', 'utf-8').toLowerCase();
      if (version.includes('microsoft') || version.includes('wsl')) {
        return 'wsl';
      }
    } catch {
      // /proc/version unreadable — treat as plain Linux
    }
    return 'linux';
  }
  console.error(`Unsupported operating system: ${process.platform}`);
  throw new ExitError(1);
}

/**
 * Return `url` with any `user:password@` userinfo removed from its authority.
 *
 * CI checkouts bake a token into the `origin` remote — for example
 * `https://x-access-token:<token>@github.com/owner/repo.git`. Anything that reads
 * the remote back and prints or publishes it (release PR links, SBOM references)
 * must drop the credential first. Only the authority is inspected, so an `@`
 * elsewhere in the URL (a path or query) is left alone, and URLs without
 * userinfo are returned unchanged.
 */
export function stripCredentials(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return url;
  }
  if (!parsed.username && !parsed.password) {
    return url;
  }
  parsed.username = '';
  parsed.password = '';
  return parsed.toString();
}

/** Return true when an executable is resolvable on PATH. */
export function which(binary) {
  const probe = process.platform === 'win32' ? 'where' : 'command -v';
  const result = spawnSync(`${probe} ${binary}`, { shell: true, stdio: 'ignore' });
  return result.status === 0;
}

/**
 * Return the shell command to open a file in the default application.
 *
 * Picks 'start' on Windows, 'open' on macOS, 'wslview' on WSL when available
 * (routes to the Windows default handler via interop), and 'xdg-open' on
 * plain Linux.
 */
export function openCommand() {
  const system = getOperatingSystem();
  if (system === 'wsl' && !which('wslview')) {
    console.log('wslview not found; install the wslu package for `open` to work. Falling back to xdg-open.');
    return OPEN_COMMAND.linux;
  }
  return OPEN_COMMAND[system];
}

/** Return the available container engine ('docker' or 'podman'). */
export function containerEngine() {
  for (const engine of ['docker', 'podman']) {
    if (which(engine)) {
      return engine;
    }
  }
  console.error('No container engine found. Install docker or podman.');
  throw new ExitError(1);
}

/** Execute a shell command with inherited stdio, throwing ExitError on failure. */
export function execute(command, { cwd, env } = {}) {
  console.log(`$ ${command}`);
  const result = spawnSync(command, {
    shell: true,
    stdio: 'inherit',
    cwd,
    env: { ...process.env, ...(env ?? {}) },
  });
  if (result.status !== 0) {
    throw new ExitError(result.status ?? 1);
  }
}

/** Run a shell command silently; return { ok, stdout, stderr } without throwing. */
export function capture(command, { cwd } = {}) {
  const result = spawnSync(command, { shell: true, encoding: 'utf-8', cwd });
  return {
    ok: result.status === 0,
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? '',
  };
}

/** Wrap a task body so it prints ✅ on success or ❌ on failure. */
export function logged(name, fn) {
  return async (...args) => {
    try {
      await fn(...args);
      console.log(`✅ ${name} passed 👍`);
    } catch (error) {
      console.log(`❌ ${name} failed 👎`);
      throw error;
    }
  };
}

/** Run all steps, accumulating failures, and throw at the end if any failed. */
export async function runSteps(steps, ...args) {
  let failed = false;
  for (const step of steps) {
    try {
      await step(...args);
    } catch {
      failed = true;
    }
  }
  if (failed) {
    throw new ExitError(1);
  }
}

/** Read and parse the root package.json. */
export function readRootPackage() {
  return JSON.parse(readFileSync('package.json', 'utf-8'));
}

/** Return true when the path exists. */
export function pathExists(path) {
  return existsSync(path);
}
