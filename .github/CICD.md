# CI/CD Pipeline Documentation

This document describes the automated CI/CD pipelines for the sqlrepository project.

## Overview

The project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline**: Runs on every push and pull request
- **Release Pipeline**: Manual workflow to publish new versions
- **Build Wheels**: Legacy support for manual GitHub releases

## CI Pipeline (`ci.yml`)

**Triggers**: Push to main/feature branches, pull requests to main

### Quality Gate Job
- **Linting**: `ruff check` for code style and common issues
- **Formatting**: `ruff format --check` for consistent code formatting
- **Type Checking**: `mypy` for static type analysis
- **Security**: `pip-audit` for vulnerability scanning

### Test Job
- **Matrix Testing**: Tests on Python 3.11 and 3.12
- **Coverage**: Generates coverage reports with pytest-cov
- **Codecov**: Uploads coverage to Codecov (Python 3.11 only)

All checks must pass before code can be merged.

## Release Pipeline (`release.yml`)

**Trigger**: Manual dispatch from GitHub Actions tab

This workflow automates the entire release process:

### 1. Version Check
- Extracts version from `pyproject.toml`
- Creates tag name (`v{version}`)
- Verifies tag doesn't already exist

### 2. Quality Gate
- Runs all quality checks (lint, format, mypy)
- Runs full test suite
- Ensures release candidates are high quality

### 3. Build Package
- Builds wheel and source distribution
- Uploads artifacts for later steps
- Validates build outputs

### 4. Create GitHub Release
- Creates git tag (`v{version}`)
- Pushes tag to repository
- Generates release notes from git commits
- Creates GitHub release with artifacts attached

### 5. Publish to PyPI
- Uses trusted publishing (no tokens needed)
- Publishes package to PyPI
- Prints SHA256 hashes for verification

### Dry Run Mode
The workflow supports a dry-run mode that:
- Runs all checks and builds
- Skips tag creation, GitHub release, and PyPI publishing
- Useful for testing the pipeline

## Release Process

### Prerequisites

1. **PyPI Trusted Publishing** must be configured:
   - Go to https://pypi.org/manage/account/publishing/
   - Add publisher: `sqlrepository`
   - Workflow: `release.yml`
   - Environment: `pypi`

2. **Update version** in `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"  # Update this
   ```

3. **Commit changes**:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 0.2.0"
   git push
   ```

### Releasing

1. Go to GitHub Actions tab
2. Select "Release" workflow
3. Click "Run workflow"
4. Choose branch (usually `main`)
5. Optionally enable "Dry run" for testing
6. Click "Run workflow"

The workflow will:
- ✅ Extract version from pyproject.toml
- ✅ Run all quality checks
- ✅ Build the package
- ✅ Create git tag (e.g., `v0.2.0`)
- ✅ Create GitHub release with notes
- ✅ Publish to PyPI

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (e.g., `1.0.0` → `2.0.0`)
- **MINOR**: New features, backward compatible (e.g., `0.1.0` → `0.2.0`)
- **PATCH**: Bug fixes, backward compatible (e.g., `0.1.0` → `0.1.1`)

## PyPI Trusted Publishing Setup

### Initial Setup (First Time Only)

1. **Create PyPI Account**: https://pypi.org/account/register/

2. **Wait for Initial Release**: You need to do a manual upload first
   ```bash
   # Build locally
   uv build
   
   # Upload with API token (one time)
   uv pip install twine
   twine upload dist/*
   ```

3. **Configure Trusted Publishing**:
   - Go to https://pypi.org/manage/project/sqlrepository/settings/publishing/
   - Add a new publisher:
     - PyPI Project Name: `sqlrepository`
     - Owner: `[your-github-username]`
     - Repository: `sql-repository`
     - Workflow: `release.yml`
     - Environment: `pypi`

4. **Configure GitHub Environment**:
   - Go to repository Settings → Environments
   - Create environment named `pypi`
   - Add protection rules (require reviewers if desired)

### Subsequent Releases

Once trusted publishing is configured, releases are fully automated - no tokens needed!

## Workflow Permissions

### CI Workflow
- `contents: read` - Read repository code
- `pull-requests: read` - Read PR information

### Release Workflow
- `contents: write` - Create tags and releases
- `id-token: write` - PyPI trusted publishing

## Troubleshooting

### Release workflow fails at "Check if tag already exists"
**Solution**: Version in `pyproject.toml` already released. Bump the version.

### PyPI publish fails with "403 Forbidden"
**Solutions**:
- Verify trusted publishing is configured correctly
- Check PyPI project name matches exactly
- Ensure GitHub environment is named `pypi`
- Verify workflow and repository names in PyPI settings

### Tests fail in CI but pass locally
**Solutions**:
- Check Python version (CI tests 3.11 and 3.12)
- Verify all dependencies in `pyproject.toml`
- Check for environment-specific issues
- Run `uv sync --all-groups` to match CI environment

### Mypy fails in CI
**Solutions**:
- Run `uv run mypy src` locally to see errors
- Add type stubs: `uv add --dev types-*`
- Add `# type: ignore` comments for unavoidable issues
- Configure mypy in `pyproject.toml` if needed

### Vulnerability scan fails
**Solutions**:
- Update vulnerable dependencies: `uv lock --upgrade-package <package>`
- Check if vulnerability is in dev dependencies (may be acceptable)
- Add exceptions in pip-audit if false positive

## Maintenance

### Adding New Quality Checks

Edit `.github/workflows/ci.yml`:
```yaml
- name: New check
  run: uv run your-tool arguments
```

### Changing Python Versions

Update matrix in `ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']  # Add/remove versions
```

### Skipping CI

Add to commit message to skip CI (use sparingly):
```
docs: update README

[skip ci]
```

## Continuous Improvement

### Recommended Additions

1. **Dependabot**: Auto-update dependencies
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

2. **Pre-commit Hooks**: Run checks before commit
   ```bash
   uv add --dev pre-commit
   # Add .pre-commit-config.yaml
   ```

3. **Changelog Generation**: Auto-generate from commits
   ```bash
   # Use conventional commits
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   ```

4. **Performance Testing**: Benchmark critical paths
   ```yaml
   - name: Benchmark
     run: uv run pytest --benchmark-only
   ```

## Best Practices

1. **Always bump version** before releasing
2. **Use dry-run** to test release pipeline
3. **Write conventional commits** for better release notes
4. **Keep workflows simple** - easier to maintain
5. **Monitor workflow runs** - fix issues promptly
6. **Test locally first** - don't rely on CI for debugging
7. **Review generated release notes** before publishing

## Support

- **GitHub Actions Logs**: Check workflow runs for detailed errors
- **PyPI Help**: https://pypi.org/help/
- **uv Documentation**: https://docs.astral.sh/uv/
- **Trusted Publishing**: https://docs.pypi.org/trusted-publishers/
