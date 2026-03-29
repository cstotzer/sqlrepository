# CI/CD Pipeline Documentation

This document describes the automated CI/CD pipelines for the sqlrepository project.

## Overview

The project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline**: Runs on every push and pull request
- **Release Pipeline**: Manual workflow to publish new versions

## CI Pipeline (`ci.yml`)

**Triggers**: Push to main/feature/bugfix/hotfix/chore branches, pull requests to main

**Concurrency**: Concurrent runs on the same ref are cancelled — only the latest run proceeds.

**Permissions**: `contents: read` at workflow level (least-privilege default).

### Quality Gate Job

Runs on a single Python version (3.11):

- **Linting**: `ruff check` for code style and common issues
- **Formatting**: `ruff format --check` for consistent code formatting
- **Type Checking**: `pyright` for static type analysis (configured via `[tool.pyright]` in `pyproject.toml`)
- **Security Scanning**: Trivy in `fs` mode, scanning for CRITICAL/HIGH vulnerabilities in dependencies, secrets, and misconfigurations. Results are uploaded to the GitHub Security tab as SARIF.

### Test Job

Matrix across all supported Python versions (3.11, 3.12, 3.13, 3.14):

- **Coverage**: Generates coverage reports with `pytest-cov`; enforces a minimum of 80% (`--cov-fail-under=80`)
- **Codecov**: Uploads coverage to Codecov (Python 3.11 only, to avoid duplicate reports)
- `fail-fast: false` ensures the full matrix always runs even if one version fails

### Composite Action

Both jobs use `.github/actions/setup-env` — a composite action that installs uv (with caching) and runs `uv sync --all-groups`. Pass `python-version` as an input to override the default (3.11).

---

## Release Pipeline (`release.yml`)

**Trigger**: Manual `workflow_dispatch` from the GitHub Actions tab

**Inputs**:
- `bump_type`: `patch` (default), `minor`, or `major`
- `dry_run`: Boolean — skips commit, tag, release, and PyPI publish when true

### Jobs

#### 1. bump-version

- Runs `uv version --bump <type>` and `uv lock` to update `pyproject.toml` and `uv.lock`
- Verifies the new tag does not already exist
- Commits and pushes the version bump (skipped in dry-run mode)
- Outputs: `version`, `tag`, `sha`

#### 2. quality-gate

- Checks out the bumped commit
- Runs ruff lint, ruff format check, pyright, and the full test suite

#### 3. build

- Builds wheel + sdist with `uv build`
- Validates artifacts with `twine check dist/*`
- Uploads artifacts for downstream jobs

#### 4. create-release

- Creates the annotated git tag and pushes it
- Generates release notes with `git cliff --latest` (grouped by conventional commit type)
- Creates the GitHub release with `gh release create`, attaching the built artifacts

#### 5. publish-pypi

- Downloads the build artifacts
- Publishes to PyPI via OIDC trusted publishing (no API token required)
- Protected by the `pypi` GitHub environment

#### dry-run-summary

Runs instead of `create-release` and `publish-pypi` when dry-run is enabled. Prints what would have been released.

---

## Release Process

### Prerequisites

1. **PyPI Trusted Publishing** must be configured:
   - Go to https://pypi.org/manage/project/sqlrepository/settings/publishing/
   - Add a new publisher:
     - PyPI Project Name: `sqlrepository`
     - Owner: `[your-github-username]`
     - Repository: `sqlrepository`
     - Workflow: `release.yml`
     - Environment: `pypi`

2. **Configure GitHub Environment**:
   - Go to repository Settings → Environments
   - Create environment named `pypi`
   - Optionally add required reviewers for an extra approval gate

3. **Codecov token** (optional but recommended):
   - Add `CODECOV_TOKEN` as a repository secret for reliable coverage uploads

### Triggering a Release

1. Go to GitHub Actions tab
2. Select the "Release" workflow
3. Click "Run workflow"
4. Choose the version bump type (`patch`, `minor`, or `major`)
5. Optionally enable "Dry run" to validate the pipeline without publishing
6. Click "Run workflow"

The workflow will automatically:
- Bump the version in `pyproject.toml` and `uv.lock`
- Run all quality checks
- Build and validate the package
- Create the git tag and GitHub release with generated release notes
- Publish to PyPI

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (e.g., `1.0.0` → `2.0.0`)
- **MINOR**: New features, backward compatible (e.g., `0.1.0` → `0.2.0`)
- **PATCH**: Bug fixes, backward compatible (e.g., `0.1.0` → `0.1.1`)

### Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) — this enables `git-cliff` to generate meaningful grouped release notes automatically:

| Prefix | Group in release notes |
|--------|------------------------|
| `feat:` | Features |
| `fix:` | Bug Fixes |
| `perf:` | Performance |
| `refactor:` | Refactoring |
| `docs:` | Documentation |
| `test:` | Testing |
| `ci:` | CI/CD |
| `chore:` | Chores |

---

## Dependency Updates (Dependabot)

`.github/dependabot.yml` configures weekly automated PRs for:
- **pip**: Python package updates (grouped by dev vs. runtime)
- **github-actions**: Action version and SHA updates

---

## Action Pinning

All third-party actions are pinned to a full commit SHA with the version tag as a comment, for example:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5  # v4.3.1
```

This prevents supply-chain attacks where a tag is retroactively updated to point at malicious code. Dependabot keeps these pins current.

---

## PyPI Trusted Publishing Setup (First Time)

If the PyPI project does not yet exist, do a one-time manual upload:

```bash
uv build
uv run twine upload dist/*
```

Then configure trusted publishing as described in the Prerequisites section above. All subsequent releases are fully automated via OIDC — no API tokens required.

---

## Workflow Permissions Summary

| Scope | CI | Release |
|-------|-----|---------|
| `contents: read` | workflow default | workflow default |
| `contents: write` | quality job: `security-events: write` | bump-version, create-release jobs |
| `id-token: write` | — | publish-pypi job only |
| `security-events: write` | quality job (SARIF upload) | — |

---

## Troubleshooting

### Release workflow fails at "Check tag availability"

The version in `pyproject.toml` has already been released. Run the workflow again — it will bump the version automatically.

### PyPI publish fails with "403 Forbidden"

- Verify trusted publishing is configured on PyPI
- Check that the PyPI project name, GitHub owner, repository name, workflow file name, and environment name all match exactly
- Ensure the `pypi` GitHub environment exists in repository settings

### Tests fail in CI but pass locally

- Check that you are testing against the same Python version
- Run `uv sync --all-groups` locally to match the exact CI environment
- Confirm your local `uv.lock` is up to date

### Pyright fails in CI

- Run `uv run pyright src` locally to reproduce errors
- Add type stubs (`uv add --dev types-<package>`) for untyped dependencies
- Use `# type: ignore` with a comment only as a last resort

### Trivy scan fails

- Update the vulnerable package: `uv lock --upgrade-package <package>`
- If the finding is in a dev-only dependency or is a false positive, add an exception in `trivy.yaml`

### Coverage falls below 80%

- The `--cov-fail-under=80` flag enforces the threshold — add tests for uncovered code paths
- Run `uv run pytest --cov=sqlrepository --cov-report=term-missing` locally to see which lines are uncovered

---

## Maintenance

### Adding New Quality Checks

Edit `.github/workflows/ci.yml` and add a step to the `quality` job:

```yaml
- name: New check
  run: uv run your-tool arguments
```

### Changing Supported Python Versions

Update the matrix in `ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13', '3.14']
```

Also update the classifiers in `pyproject.toml`.

### Skipping CI

Add to the commit message body (use sparingly):

```
docs: update README

[skip ci]
```
