"""Per-axis invariants over the cartesian product of copier answer combinations.

Each test below receives one generated project per matrix cell via the
``generated_project`` fixture in ``conftest.py``. Adding a new assertion is one
new ``test_*`` function; adding a new combo axis edits ``matrix_combos()`` in
``_CI/configuration.py`` and both the pytest suite and the matrix runner pick
it up automatically.
"""

import json
import os
import subprocess

import pytest

from _CI.configuration import PROJECT_SLUG


def test_host_scaffolding_present(generated_project):
    """`.github/workflows/` ships only for github; `.gitlab-ci.yml` ships only for gitlab."""
    project, cell = generated_project
    if cell['git_hosting_service'] == 'github':
        assert (project / '.github' / 'workflows').is_dir()
        assert not (project / '.gitlab-ci.yml').exists()
    else:
        assert not (project / '.github').exists()
        assert (project / '.gitlab-ci.yml').exists()


def test_host_submodule_present(generated_project):
    """`_CI/tasks/<host>.mjs` is present for the chosen host and absent for the other."""
    project, cell = generated_project
    chosen_name = cell['git_hosting_service']
    other_name = 'gitlab' if chosen_name == 'github' else 'github'
    assert (project / '_CI' / 'tasks' / f'{chosen_name}.mjs').exists()
    assert not (project / '_CI' / 'tasks' / f'{other_name}.mjs').exists()


def test_release_imports_chosen_host(generated_project):
    """`release.mjs` imports the helpers of the chosen host module."""
    project, cell = generated_project
    release_mjs = (project / '_CI' / 'tasks' / 'release.mjs').read_text(encoding='utf-8')
    assert f"./{cell['git_hosting_service']}.mjs" in release_mjs


def test_pages_workflow_matches_choice(generated_project):
    """`pages.yaml` ships iff integrate_pages=true AND the host is github."""
    project, cell = generated_project
    expected = cell['integrate_pages'] and cell['git_hosting_service'] == 'github'
    assert (project / '.github' / 'workflows' / 'pages.yaml').exists() == expected


def test_pages_task_definition_matches_choice(generated_project):
    """`deployGithub` is defined iff integrate_pages=true AND the host is github."""
    project, cell = generated_project
    expected = cell['integrate_pages'] and cell['git_hosting_service'] == 'github'
    document_mjs = (project / '_CI' / 'tasks' / 'document.mjs').read_text(encoding='utf-8')
    assert ('deployGithub' in document_mjs) == expected


def test_dependency_track_imports_match_choice(generated_project):
    """`OWASP_DTRACK_SETTINGS` is referenced by secure.mjs iff integrate_dependency_track=true."""
    project, cell = generated_project
    secure_mjs = (project / '_CI' / 'tasks' / 'secure.mjs').read_text(encoding='utf-8')
    assert ('OWASP_DTRACK_SETTINGS' in secure_mjs) == cell['integrate_dependency_track']


def test_root_package_json_is_valid(generated_project):
    """The generated root package.json parses cleanly and carries the expected blocks."""
    project, _ = generated_project
    data = json.loads((project / 'package.json').read_text(encoding='utf-8'))
    assert data['name'] == PROJECT_SLUG
    assert data['private'] is True
    assert 'commit-and-tag-version' in data
    assert data['engines']['node'].startswith('>=')


def test_workspace_package_json_files_are_valid(generated_project):
    """Every workspace package.json parses and scopes its name under the project slug."""
    project, _ = generated_project
    for package in ('apps/api', 'apps/web', 'packages/shared'):
        data = json.loads((project / package / 'package.json').read_text(encoding='utf-8'))
        assert data['name'].startswith(f'@{PROJECT_SLUG}/')
        assert 'typecheck' in data['scripts']


def test_json_configs_are_valid(generated_project):
    """Static JSON configs render/copy into parseable JSON."""
    project, _ = generated_project
    for config in ('biome.json', 'knip.json', 'typedoc.json', 'tsconfig.base.json'):
        json.loads((project / config).read_text(encoding='utf-8'))


def test_node_version_is_rendered(generated_project):
    """`.node-version` carries the chosen Node major version."""
    project, cell = generated_project
    assert (project / '.node-version').read_text(encoding='utf-8').strip() == '24'


def test_workflow_cmd_is_executable(generated_project):
    """The polyglot launcher has the executable bit so `./workflow.cmd …` works on Unix."""
    project, _ = generated_project
    assert os.access(project / 'workflow.cmd', os.X_OK)


def test_workflow_runner_lists_tasks(generated_project):
    """`node _CI/workflow.mjs` runs on the generated tree and prints the task list."""
    project, _ = generated_project
    result = subprocess.run(
        ['node', '_CI/workflow.mjs', '--list'],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    )
    for namespace in ('bootstrap', 'format', 'lint', 'test', 'build', 'quality', 'secure', 'release', 'document'):
        assert namespace in result.stdout


def test_scaffold_tests_are_present(generated_project):
    """Both apps ship a scaffolded test suite."""
    project, _ = generated_project
    assert (project / 'apps' / 'api' / 'tests' / 'app.test.ts').exists()
    assert (project / 'apps' / 'web' / 'tests' / 'App.test.tsx').exists()


@pytest.mark.parametrize('license_choice', ['Apache-2.0', 'MIT', 'BSD-3-Clause', 'None'])
def test_license_file_matches_choice(template_snapshot, tmp_path_factory, license_choice):
    """Each license choice produces (or skips) a LICENSE file at the project root."""
    workdir = tmp_path_factory.mktemp(f'license-{license_choice}')
    data_file = workdir / 'data.json'
    data_file.write_text(json.dumps({'license': license_choice}), encoding='utf-8')
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
    if license_choice == 'None':
        assert not (project / 'LICENSE').exists()
        license_field_expected = False
    else:
        assert (project / 'LICENSE').exists()
        license_field_expected = True
    package = json.loads((project / 'package.json').read_text(encoding='utf-8'))
    assert ('license' in package) == license_field_expected
    assert not (project / 'licenses').exists()
