# CLAUDE.md — sqlrepository

A Python repository pattern implementation for SQLAlchemy and SQLModel, inspired by Spring Data JPA repositories. Provides type-safe, zero-boilerplate CRUD operations with sync and async support.

**Current version**: derived from git tags (see `git describe --tags`)
**License**: GPL-3.0
**Python**: >= 3.11

---

## Development Commands

This project uses **uv** for dependency management.

```bash
# Install all dependencies (including optional groups)
uv sync --all-groups

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=sqlrepository --cov-report=term-missing

# Run a specific test file or test
uv run pytest tests/sqlalchemy/test_repository.py -v
uv run pytest tests/sqlalchemy/test_repository.py::test_find_by_id -v

# Lint
uv run ruff check src tests

# Format
uv run ruff format src tests

# Type check
uv run pyright src
```

---

## Project Structure

```
sqlrepository/
├── .github/
│   ├── instructions.md              # Detailed contributor guide
│   ├── CICD.md                      # CI/CD pipeline documentation
│   ├── copilot-skills/
│   │   ├── chore.instructions.md
│   │   └── release.instructions.md
│   ├── actions/
│   │   └── setup-env/action.yml     # Composite action: setup-uv + uv sync
│   ├── dependabot.yml               # Automated github-actions version updates
│   └── workflows/
│       ├── ci.yml                   # Quality checks + tests on push/PR
│       ├── release.yml              # Release on vX.Y.Z tag push
│       └── update-deps.yml          # Weekly uv lock --upgrade PR
├── src/sqlrepository/
│   ├── __init__.py                  # Exports: Repository, AsyncRepository, EntityType, IdType
│   ├── core.py                      # Sync repository (SQLAlchemy DeclarativeBase)
│   ├── asyncio.py                   # Async repository (SQLAlchemy AsyncSession)
│   └── sqlmodel.py                  # SQLModel-specific Repository and AsyncRepository
├── tests/
│   ├── conftest.py                  # Shared fixtures and JSON data loading
│   ├── resources/
│   │   ├── artists.json             # Test artist data (6 records)
│   │   └── albums.json              # Test album data
│   ├── sqlalchemy/
│   │   ├── conftest.py              # SQLAlchemy fixtures (in-memory SQLite)
│   │   ├── models.py                # Test models: Artist, Album
│   │   ├── repositories.py          # Test repository implementations
│   │   ├── test_repository.py       # Sync CRUD tests
│   │   ├── test_async_repository.py # Async CRUD tests
│   │   ├── test_special_cases.py    # Edge cases / error handling
│   │   └── test_generics.py         # Generic type parameter tests
│   └── sqlmodel/
│       ├── conftest.py              # SQLModel fixtures
│       ├── models.py                # SQLModel test models
│       ├── repositories.py          # SQLModel test repositories
│       ├── test_repository.py       # Sync SQLModel tests
│       ├── test_async_repository.py # Async SQLModel tests
│       ├── test_special_cases.py
│       └── test_generics.py
├── pyproject.toml                   # Build config, dependencies, tool config
├── uv.lock                          # Locked dependencies
├── README.md                        # User-facing documentation with examples
├── trivy.yaml                       # Security scanning config
└── LICENSE
```

---

## Architecture

### Module Layout

| File | Purpose |
|------|---------|
| `core.py` | `BaseRepository` mixin + `Repository[EntityType, IdType]` for SQLAlchemy `DeclarativeBase` models |
| `asyncio.py` | `BaseAsyncRepository` mixin + `AsyncRepository[EntityType, IdType]` for `AsyncSession` |
| `sqlmodel.py` | `Repository[EntityType, IdType]` and `AsyncRepository[EntityType, IdType]` for SQLModel models |
| `__init__.py` | Re-exports `Repository` (from `core`), `AsyncRepository` (from `asyncio`), `EntityType`, `IdType` |

> **Note**: `sqlmodel.py` exports its own `Repository` and `AsyncRepository` — these are different classes from the ones in `core.py`/`asyncio.py`. SQLModel users import from `sqlrepository.sqlmodel`, not from `sqlrepository` directly.

### Type Inference via `__init_subclass__`

Both sync and async repositories automatically extract the model type from the generic parameters:

```python
class ArtistRepository(Repository[Artist, int]):
    pass  # cls._model_type is automatically set to Artist
```

`__init_subclass__` inspects `__orig_bases__` to extract the first generic argument.

### Available CRUD Methods

All repository classes expose the same interface:

| Method | Description |
|--------|-------------|
| `save(entity)` | Insert or merge entity; flushes to get generated IDs |
| `save_all(entities)` | Save a collection of entities |
| `find_by_id(id)` | Return entity or `None` |
| `find_all()` | Return all entities |
| `find_all_by_id(ids)` | Return entities matching any of the given IDs |
| `exists_by_id(id)` | Return `bool` |
| `count()` | Return total row count |
| `delete(entity)` | Remove a specific entity |
| `delete_by_id(id)` | Remove by primary key |
| `delete_all(entities)` | Remove a collection |
| `delete_all_by_id(ids)` | Remove by list of IDs |

Async versions of all methods are `async def` and must be `await`ed.

### Session Management

- Repositories receive a `Session` (sync) or `AsyncSession` (async) at construction time.
- **Transaction boundaries are the caller's responsibility** — repositories never commit, rollback, or expose transaction control methods.
- Repositories do internal `flush()` calls where needed (e.g., to populate auto-generated primary keys after `save()`).

---

## Code Conventions

### Style

- **Line length**: 79 characters, enforced by Ruff
- **Formatter**: `ruff format`
- **Linter**: `ruff check` with `ALL` rules enabled (see `pyproject.toml` for specific ignores)
- **Type checker**: `pyright` (configured via `[tool.pyright]` in `pyproject.toml`, targets Python 3.11, checks `src/`)
- **Docstring style**: Google style — required on all public methods and classes
- **Type hints**: Required on all public method signatures

### Naming

- **Classes**: PascalCase — `ArtistRepository`, `AsyncRepository`
- **Methods**: snake_case — `find_by_id`, `save_all`
- **Private methods/attributes**: leading underscore — `_model_type`
- **TypeVars**: `EntityType` (bound to `DeclarativeBase`), `IdType` (primary key type)

### Validation

All repository methods raise `ValueError` for `None` inputs:

```python
if entity is None:
    raise ValueError("entity must not be None")
```

### Docstring Template

```python
def find_by_id(self, id: IdType) -> EntityType | None:
    """Retrieves an entity by its id.

    Args:
        id (IdType): The identifier of the entity. Must not be None.

    Returns:
        EntityType | None: The entity with the given id, or None if not found.

    Raises:
        ValueError: If id is None.
    """
```

---

## Testing

### Structure

Tests are split into two parallel suites:

- `tests/sqlalchemy/` — tests against SQLAlchemy `DeclarativeBase` models
- `tests/sqlmodel/` — tests against SQLModel models

Both use **in-memory SQLite** databases. Each test function gets a fresh session via fixtures in the respective `conftest.py`.

### Key Fixtures

- `artist_repository` — a sync `ArtistRepository` bound to a fresh in-memory DB
- `async_artist_repository` — an async `AsyncArtistRepository` with `expire_on_commit=False`
- Test data is loaded from `tests/resources/artists.json` and `albums.json`

### Async Test Pattern

```python
import pytest

@pytest.mark.asyncio
async def test_save_entity(async_artist_repository):
    artist = Artist(name="Led Zeppelin", genre=Genre.ROCK, is_active=True)
    saved = await async_artist_repository.save(artist)
    await async_artist_repository.session.commit()
    assert saved.id is not None
```

**Always use `expire_on_commit=False`** in async session fixtures to prevent lazy-load errors after commit:

```python
AsyncSession(engine, expire_on_commit=False)
```

### Running Subset of Tests

```bash
uv run pytest tests/sqlalchemy -v        # SQLAlchemy suite only
uv run pytest tests/sqlmodel -v          # SQLModel suite only
uv run pytest -k "test_find_by_id" -v   # Any test matching pattern
```

---

## Dependencies

### Core (always required)

```
sqlalchemy >= 2.0.46, < 3.0.0
```

### Optional Groups

| Group | Extra package | When needed |
|-------|--------------|-------------|
| `sqlmodel` | `sqlmodel >= 0.0.34, < 0.1.0` | Using `sqlrepository.sqlmodel` |
| `async` | `greenlet >= 3.2.0, < 4.0.0` | Using async repositories |

### Dev Group

Includes everything: pytest, pytest-asyncio, pytest-cov, ruff, pyright, sqlmodel, aiosqlite, greenlet, twine, git-cliff.

### Constraint Notes

- **pytest < 9** is required because `pytest-asyncio 0.26.x` does not support pytest 9 yet.
- `aiosqlite` is a dev-only dependency (async SQLite driver used in tests).
- Use `pytest-cov` (not `pytest-coverage` — different package) for the `--cov` flags.

---

## CI/CD

### Workflows

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `ci.yml` | Push / PR to `main` | ruff lint → ruff format check → pyright → Trivy scan (SARIF) → pytest (Python 3.11–3.14) → Codecov upload |
| `release.yml` | Push of `v*` tag | Quality gate → build wheel+sdist → twine check → GitHub release (git-cliff notes) → publish to PyPI |
| `update-deps.yml` | Weekly (Monday 06:00 UTC) | `uv lock --upgrade` → open PR if lock file changed |

### Release Process

The version is derived from the git tag at build time (`hatch-vcs`) — no version file to edit. Push a tag and the workflow handles the rest:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The `release.yml` workflow triggers automatically on the tag push and handles the GitHub release and PyPI publishing.

> **Dry run**: Trigger `release.yml` manually via `workflow_dispatch` with `dry_run: true` to verify quality gate and build without publishing.

See `.github/CICD.md` for full details.

### Security

- All third-party GitHub Actions are pinned to commit SHAs (with version comments).
- Trivy scans for CRITICAL/HIGH vulnerabilities and uploads results to the GitHub Security tab as SARIF.
- Dependabot keeps GitHub Actions SHA pins current (weekly).
- `update-deps.yml` keeps Python dependencies current via weekly `uv lock --upgrade` PRs.
- Coverage must meet an 80% threshold (`--cov-fail-under=80`) or CI fails.

### Commit Prefixes (Conventional Commits)

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation changes |
| `chore:` | Maintenance (CI, version bumps, deps) |
| `test:` | Test changes |
| `refactor:` | Code restructuring without behavior change |

---

## Common Tasks

### Adding a New Repository Method

1. Add to `BaseRepository` (in `core.py`) and `BaseAsyncRepository` (in `asyncio.py`) — the async version must be `async def` and use `await` on all session calls.
2. If the method applies to SQLModel, verify it works via the `sqlmodel.py` classes (they delegate to the same base mixins).
3. Write tests in both `tests/sqlalchemy/` and `tests/sqlmodel/`.
4. Add a Google-style docstring.

### Adding a New Feature

1. Create a branch: `git checkout -b feature/my-feature`
2. Implement with tests (TDD recommended)
3. Update `README.md` with usage examples
4. Run: `uv run pytest && uv run ruff check src tests && uv run ruff format src tests && uv run pyright src`
5. Commit with conventional commit message

### Checking Security

Trivy scans for CRITICAL and HIGH severity vulnerabilities in dependencies, secrets, and misconfigurations:

```bash
trivy fs --config trivy.yaml .
```

---

## Design Decisions

### Why Separate Classes for SQLAlchemy vs SQLModel?

SQLModel does not inherit from SQLAlchemy's `DeclarativeBase`, making `Union[DeclarativeBase, SQLModel]` bounds problematic for mypy and Pylance. The solution is separate classes (`core.py` / `sqlmodel.py`) sharing implementation via base mixins. This provides correct type inference and IDE autocomplete for both ORM variants.

### Why Not Expose Commit/Rollback?

Following the Spring Data JPA pattern: repositories are responsible for data access only. Transaction lifecycle belongs to the service/use-case layer. This makes repositories composable within a single transaction without unintended side effects.
