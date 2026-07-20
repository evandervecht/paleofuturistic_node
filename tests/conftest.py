"""Shared fixtures for the template invariants suite."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def find_repo_root() -> Path:
    """Walk up from this file until a directory containing ``copier.yml`` is found."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / 'copier.yml').is_file():
            return candidate
    raise RuntimeError("Could not locate repo root: no 'copier.yml' found above conftest.py")


REPO_ROOT = find_repo_root()
sys.path.insert(0, str(REPO_ROOT))

from _CI.configuration import IGNORE_PATTERNS, PROJECT_SLUG, combo_context, matrix_combos  # noqa: E402


@pytest.fixture(scope='session')
def template_snapshot(tmp_path_factory):
    """Snapshot the parent template into a plain temp dir so copier sees every current file.

    Copier copies happily from a non-git local directory, so no git init/commit is needed.
    """
    snapshot = tmp_path_factory.mktemp('template') / 'repo'
    shutil.copytree(REPO_ROOT, snapshot, ignore=IGNORE_PATTERNS)
    return snapshot


@pytest.fixture(scope='session', params=matrix_combos(), ids=lambda cell: cell['label'])
def generated_project(request, template_snapshot, tmp_path_factory):
    """Generate the template for one matrix cell with copier. Cached per-cell for the session."""
    cell = request.param
    workdir = tmp_path_factory.mktemp(cell['label'])
    data = combo_context(
        git_hosting_service=cell['git_hosting_service'],
        integrate_dependency_track=cell['integrate_dependency_track'],
        integrate_pages=cell['integrate_pages'],
    )
    data_file = workdir / 'data.json'
    data_file.write_text(json.dumps(data), encoding='utf-8')
    # Name the destination after the slug so `project.name` yields the package slug for tests.
    project = workdir / PROJECT_SLUG
    subprocess.run(
        [
            'uvx',
            'copier',
            'copy',
            '--defaults',
            '--trust',
            '--data-file',
            str(data_file),
            str(template_snapshot),
            str(project),
        ],
        check=True,
        capture_output=True,
    )
    return project, cell
