"""Template QA task runner for the template repository itself.

Invoked via ``./workflow.cmd <command>`` (which wraps ``uv run --group dev
python _CI/tasks.py``). Commands mirror the paleofuturistic_python template's
dev entry points:

* ``test.invariants`` — fast pytest layer over the generated matrix cells
* ``test``            — generate with default context and run the full inner QA cycle
* ``test.combo``      — same as ``test`` for one explicit matrix cell
* ``test.matrix``     — every cell of the cartesian product, logs in reports/matrix/
* ``test.list-combos``— print the matrix (``--as-json`` for CI fan-out)
"""

import argparse
import concurrent.futures
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Windows consoles default to a legacy codepage that cannot encode the ✅/❌
# banners; force UTF-8 with replacement so logging never crashes a run.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, 'reconfigure', None)
    if _reconfigure is not None:
        _reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _CI import PROJECT_ROOT_DIRECTORY, emojize_message
from _CI.configuration import (IGNORE_PATTERNS,
                               PROJECT_SLUG,
                               QA_STEPS,
                               TEMPLATE_SECURITY_OVERRIDE_ENV,
                               combo_context,
                               combo_label,
                               matrix_combos,
                               read_template_overrides,
                               security_override_env_var)

REPORTS_DIR = PROJECT_ROOT_DIRECTORY / 'reports' / 'matrix'

# The explicit directory prefix matters on both platforms: POSIX shells never
# search the cwd, and hardened Windows hosts set NoDefaultCurrentDirectoryInExePath.
WORKFLOW_LAUNCHER = '.\\workflow.cmd' if platform.system() == 'Windows' else './workflow.cmd'


def run_command(cmd, cwd=None, env=None, log_file=None):
    """Run a shell command. Return True on exit 0. Stream to log_file if given, else stdout.

    `VIRTUAL_ENV` is stripped from the inherited environment so each combo's
    generated project sees a clean slate.
    """
    inherited = {key: value for key, value in os.environ.items() if key != 'VIRTUAL_ENV'}
    proc_env = {**inherited, **(env or {})}
    cwd_str = str(cwd) if cwd else None
    if log_file is not None:
        with log_file.open('a', encoding='utf-8') as handle:
            handle.write(f'\n$ {cmd}\n')
            handle.flush()
            result = subprocess.run(cmd, shell=True, cwd=cwd_str, env=proc_env,
                                    stdout=handle, stderr=subprocess.STDOUT)
    else:
        print(f'\n$ {cmd}', flush=True)
        result = subprocess.run(cmd, shell=True, cwd=cwd_str, env=proc_env)
    return result.returncode == 0


def prepare_snapshot(tmpdir):
    """Copy the template into a plain temp dir so copier sees all current files.

    Copier copies happily from a non-git local directory, so no git snapshot is needed.
    """
    template_repo = tmpdir / 'template'
    shutil.copytree(str(PROJECT_ROOT_DIRECTORY), str(template_repo), ignore=IGNORE_PATTERNS)
    return template_repo


def run_combo(template_repo, output_root, extra_context, label, log_file=None):
    """Generate the template with extra_context and run QA_STEPS. Return True on success."""
    combo_root = output_root / label
    combo_root.mkdir(parents=True, exist_ok=True)

    data_file = combo_root / 'data.json'
    data_file.write_text(json.dumps(extra_context or {}), encoding='utf-8')
    project_dir = combo_root / 'generated' / PROJECT_SLUG
    copier_cmd = (
        f'uvx copier copy --defaults --trust '
        f'--data-file "{data_file}" "{template_repo}" "{project_dir}"'
    )
    if not run_command(copier_cmd, log_file=log_file):
        return False

    init_steps = (
        'git init -b main',
        'git add -A',
        ('git -c commit.gpgsign=false -c user.name=ci -c user.email=ci@localhost '
         'commit -m "feat: initial project from template" '
         '--author "ci <ci@localhost>"'),
    )
    for step in init_steps:
        if not run_command(step, cwd=project_dir, log_file=log_file):
            return False

    step_env = {'CI': 'true'}
    override_parts = []
    file_overrides = read_template_overrides()
    if file_overrides:
        override_parts.append(file_overrides)
    env_override = os.environ.get(TEMPLATE_SECURITY_OVERRIDE_ENV, '').strip()
    if env_override:
        override_parts.append(env_override)
    if override_parts:
        step_env[security_override_env_var()] = ','.join(override_parts)

    for step in QA_STEPS:
        if not run_command(f'{WORKFLOW_LAUNCHER} {step}', cwd=project_dir, env=step_env, log_file=log_file):
            failure_msg = f'[{label}] task "{step}" failed'
            if log_file is not None:
                with log_file.open('a', encoding='utf-8') as handle:
                    handle.write(f'\n{failure_msg}\n')
            else:
                print(emojize_message(failure_msg, success=False))
            return False
    return True


def test(args):
    """Generate the template with default context and run the full QA cycle."""
    tmpdir = Path(tempfile.mkdtemp(prefix='paleofuturistic_test_'))
    try:
        template_repo = prepare_snapshot(tmpdir)
        output_root = tmpdir / 'generated'
        output_root.mkdir()
        ok = run_combo(template_repo, output_root, extra_context={}, label='default')
        if not ok:
            print(emojize_message('Template QA failed', success=False))
            raise SystemExit(1)
        print(emojize_message('All template QA tasks passed successfully'))
    finally:
        shutil.rmtree(str(tmpdir), ignore_errors=True)


def combo(args):
    """Run the full QA cycle for one matrix cell across all three template knobs."""
    tmpdir = Path(tempfile.mkdtemp(prefix='paleofuturistic_combo_'))
    try:
        template_repo = prepare_snapshot(tmpdir)
        output_root = tmpdir / 'generated'
        output_root.mkdir()
        label = combo_label(
            git_hosting_service=args.git_hosting_service,
            integrate_dependency_track=args.integrate_dependency_track,
            integrate_pages=args.integrate_pages,
        )
        ok = run_combo(
            template_repo,
            output_root,
            extra_context=combo_context(
                git_hosting_service=args.git_hosting_service,
                integrate_dependency_track=args.integrate_dependency_track,
                integrate_pages=args.integrate_pages,
            ),
            label=label,
        )
        if not ok:
            print(emojize_message(f'Combo {label} failed', success=False))
            raise SystemExit(1)
        print(emojize_message(f'Combo {label} passed'))
    finally:
        shutil.rmtree(str(tmpdir), ignore_errors=True)


def matrix(args):
    """Run every matrix cell; summarize and exit non-zero on any failure.

    Defaults to sequential (workers=1) because each combo internally runs
    pnpm install + parallel vitest workers, so running combos in parallel on a
    single host over-subscribes CPU. On GitHub Actions each matrix cell runs on
    its own VM, so the outer parallelism is handled by the fan-out workflow.
    """
    combos = matrix_combos()
    effective_workers = max(1, min(len(combos), args.workers))

    tmpdir = Path(tempfile.mkdtemp(prefix='paleofuturistic_matrix_'))
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        template_repo = prepare_snapshot(tmpdir)
        output_root = tmpdir / 'generated'
        output_root.mkdir()

        def worker(cell):
            label = cell['label']
            log_path = REPORTS_DIR / f'{label}.log'
            if log_path.exists():
                log_path.unlink()
            start = time.monotonic()
            try:
                ok = run_combo(
                    template_repo,
                    output_root,
                    extra_context=combo_context(
                        git_hosting_service=cell['git_hosting_service'],
                        integrate_dependency_track=cell['integrate_dependency_track'],
                        integrate_pages=cell['integrate_pages'],
                    ),
                    label=label,
                    log_file=log_path,
                )
            except Exception as exc:  # worker must not crash the pool
                with log_path.open('a', encoding='utf-8') as handle:
                    handle.write(f'\nEXCEPTION: {exc}\n')
                ok = False
            return label, ok, time.monotonic() - start

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=effective_workers) as pool:
            for outcome in pool.map(worker, combos):
                results.append(outcome)

        print()
        print(f'{"combo":<12} {"result":<7} duration')
        any_failed = False
        for label, ok, duration in results:
            mins, secs = divmod(int(duration), 60)
            status = 'PASS' if ok else 'FAIL'
            log_hint = '' if ok else f'  (log: {REPORTS_DIR.relative_to(PROJECT_ROOT_DIRECTORY)}/{label}.log)'
            print(f'{label:<12} {status:<7} {mins}m{secs:02d}s{log_hint}')
            any_failed = any_failed or not ok

        if any_failed:
            print(emojize_message('Matrix had failing combos', success=False))
            raise SystemExit(1)
        print(emojize_message('All matrix combos passed'))
    finally:
        shutil.rmtree(str(tmpdir), ignore_errors=True)


def list_combos(args):
    """Print the matrix — table by default, JSON array with --as-json."""
    combos = matrix_combos()
    if args.as_json:
        print(json.dumps(combos, separators=(',', ':')))
        return
    print(f'{"label":<18} {"host":<7} {"dep_track":<10} {"pages":<6}')
    for cell in combos:
        print(
            f'{cell["label"]:<18} '
            f'{cell["git_hosting_service"]:<7} '
            f'{str(cell["integrate_dependency_track"]):<10} '
            f'{str(cell["integrate_pages"]):<6}'
        )


def invariants(args):
    """Run the fast pytest invariants against the cartesian-product matrix."""
    if not run_command('uv run --group test pytest tests/ -v', cwd=PROJECT_ROOT_DIRECTORY):
        print(emojize_message('Template invariants failed', success=False))
        raise SystemExit(1)
    print(emojize_message('Template invariants passed'))


def str2bool(value):
    """Parse a CLI boolean flag value."""
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('test.invariants', help='Fast pytest layer over generated matrix cells').set_defaults(fn=invariants)
    sub.add_parser('test', help='Generate with default context; run the full inner QA cycle').set_defaults(fn=test)

    combo_parser = sub.add_parser('test.combo', help='Full QA cycle for one explicit matrix cell')
    combo_parser.add_argument('--git-hosting-service', default='github', choices=('github', 'gitlab'))
    combo_parser.add_argument('--integrate-dependency-track', type=str2bool, default=True)
    combo_parser.add_argument('--no-integrate-dependency-track', dest='integrate_dependency_track',
                              action='store_false')
    combo_parser.add_argument('--integrate-pages', type=str2bool, default=True)
    combo_parser.add_argument('--no-integrate-pages', dest='integrate_pages', action='store_false')
    combo_parser.set_defaults(fn=combo)

    matrix_parser = sub.add_parser('test.matrix', help='Run every cell of the cartesian product')
    matrix_parser.add_argument('--workers', type=int, default=1)
    matrix_parser.set_defaults(fn=matrix)

    list_parser = sub.add_parser('test.list-combos', help='Print the matrix')
    list_parser.add_argument('--as-json', action='store_true')
    list_parser.set_defaults(fn=list_combos)

    args = parser.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
