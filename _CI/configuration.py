"""Centralized constants for the template repository's dev tasks."""

import shutil

import yaml

from _CI import PROJECT_ROOT_DIRECTORY

PROJECT_SLUG = 'paleofuturistic-node-project'
IGNORE_PATTERNS = shutil.ignore_patterns(
    '.git', '.venv', 'node_modules', '__pycache__', '*.pyc', '.copier-answers.yml', 'reports'
)
QA_STEPS = ('format', 'lint', 'test', 'build', 'quality', 'document')
TEMPLATE_SECURITY_OVERRIDE_ENV = 'TEMPLATE_SECURITY_OVERRIDE'
SECURITY_OVERRIDES_FILE = PROJECT_ROOT_DIRECTORY / '.security-overrides'


def read_template_overrides() -> str:
    """Return comma-joined entries from the parent `.security-overrides` file.

    Entries are validated and parsed by the inner template's `secure.audit`
    task when the merged string is forwarded via `<PROJECT>_SECURITY_OVERRIDE`,
    so the parent only needs to strip `#` comments and blank lines.
    """
    if not SECURITY_OVERRIDES_FILE.exists():
        return ''
    entries = []
    for raw in SECURITY_OVERRIDES_FILE.read_text(encoding='utf-8').splitlines():
        entry = raw.split('#', 1)[0].strip()
        if entry:
            entries.append(entry)
    return ','.join(entries)


def security_override_env_var() -> str:
    """Env var name the generated project's secure.audit task reads."""
    slug_upper = PROJECT_SLUG.upper().replace('-', '_').replace('.', '_')
    return f'{slug_upper}_SECURITY_OVERRIDE'


def base_context() -> dict:
    """Default context: the newest supported Node version from copier.yml's choices."""
    copier_data = yaml.safe_load((PROJECT_ROOT_DIRECTORY / 'copier.yml').read_text(encoding='utf-8'))
    known_versions = sorted(copier_data['node_version']['choices'], key=int)
    return {'node_version': known_versions[-1]}


def combo_context(*, git_hosting_service: str, integrate_dependency_track: bool, integrate_pages: bool) -> dict:
    """Matrix-cell context: newest Node version plus the three binary template knobs."""
    return {
        **base_context(),
        'git_hosting_service': git_hosting_service,
        'integrate_dependency_track': integrate_dependency_track,
        'integrate_pages': integrate_pages,
    }


def combo_label(*, git_hosting_service: str, integrate_dependency_track: bool, integrate_pages: bool) -> str:
    """Stable short label for log files and CI job names: e.g. ``gh-dep1-pages0``."""
    host_short = 'gh' if git_hosting_service == 'github' else 'gl'
    return f'{host_short}-dep{int(integrate_dependency_track)}-pages{int(integrate_pages)}'


def matrix_combos() -> list[dict]:
    """Cartesian product over git_hosting_service x integrate_dependency_track x integrate_pages."""
    return [
        {
            'label': combo_label(
                git_hosting_service=host,
                integrate_dependency_track=dep_track,
                integrate_pages=pages,
            ),
            'git_hosting_service': host,
            'integrate_dependency_track': dep_track,
            'integrate_pages': pages,
        }
        for host in ('github', 'gitlab')
        for dep_track in (False, True)
        for pages in (False, True)
    ]
