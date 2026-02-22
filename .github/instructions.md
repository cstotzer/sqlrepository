# sqlrepository - GitHub Copilot Instructions

A Python repository pattern implementation for SQLAlchemy and SQLModel, inspired by Spring Data's JPA Repositories.

## Project Overview

**sqlrepository** provides a clean, type-safe repository pattern for database operations with both synchronous and asynchronous support. It supports:
- ✅ SQLAlchemy DeclarativeBase models
- ✅ SQLModel models with Pydantic validation
- ✅ Async/await with AsyncRepository
- ✅ Type-safe generic repositories
- ✅ Zero-boilerplate CRUD operations

## Build, Test, and Lint

This project uses **uv** for dependency management.

```bash
# Install dependencies (including optional groups)
uv sync --all-groups

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=sqlrepository --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_repository.py -v

# Run specific test
uv run pytest tests/test_repository.py::test_find_by_id -v

# Run async tests only
uv run pytest tests/test_async_repository.py tests/test_async_sqlmodel_repository.py -v

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check with mypy
uv run mypy src/sqlrepository
```

## Architecture

### Core Design: Mixin Pattern with Separate Repository Classes

The project uses a **mixin pattern** to share CRUD implementation while maintaining clean separation between different repository types:

#### Synchronous Repositories (`src/sqlrepository/core.py`)

```
_RepositoryMixin[EntityType, IdType]
├── All CRUD operations (save, find, delete, count, etc.)
├── Uses: Session (sync)
│
├── Repository[EntityType, IdType]
│   ├── For: SQLAlchemy DeclarativeBase models
│   ├── Bound: EntityType extends DeclarativeBase
│   └── Example: Repository[Artist, int]
│
└── SQLModelRepository[SQLModelEntityType, IdType]
    ├── For: SQLModel models
    ├── Bound: SQLModelEntityType extends SQLModel
    └── Example: SQLModelRepository[Artist, int]
```

#### Asynchronous Repositories (`src/sqlrepository/async_repository.py`)

```
_AsyncRepositoryMixin[EntityType, IdType]
├── All async CRUD operations (async save, async find, etc.)
├── Uses: AsyncSession (async)
│
├── AsyncRepository[EntityType, IdType]
│   ├── For: SQLAlchemy DeclarativeBase models
│   ├── Bound: EntityType extends DeclarativeBase
│   └── Example: AsyncRepository[Artist, int]
│
└── AsyncSQLModelRepository[SQLModelEntityType, IdType]
    ├── For: SQLModel models
    ├── Bound: SQLModelEntityType extends SQLModel
    └── Example: AsyncSQLModelRepository[Artist, int]
```

### Key Implementation Details

#### Type Inference via `__init_subclass__`

Both sync and async repositories use `__init_subclass__` to automatically extract the model type from generic parameters:

```python
class ArtistRepository(Repository[Artist, int]):
    pass  # cls.model is automatically set to Artist
```

The `__init_subclass__` method inspects `__orig_bases__` and extracts the first generic argument.

#### Session Management

- **Sync**: Repositories receive a `Session` in `__init__`
- **Async**: Repositories receive an `AsyncSession` in `__init__`
- **Transaction control is the caller's responsibility** (no commit/flush/rollback methods exposed)
- Repositories perform internal flush operations as needed (e.g., to get generated IDs)
- This follows the Spring Data JPA pattern of separation of concerns

#### Async Considerations

- All async repository methods use `await`
- Entity refresh after save: `await session.refresh(entity)` to avoid detached state
- Delete operations: `await session.delete(entity)` (async in SQLAlchemy 2.0+)
- **Important**: Use `AsyncSession(engine, expire_on_commit=False)` to avoid lazy-loading issues after commit

### Custom Repository Methods

#### Synchronous Custom Methods

```python
from sqlalchemy import select
from sqlrepository import Repository

class ArtistRepository(Repository[Artist, int]):
    def find_by_name(self, name: str) -> list[Artist]:
        """Find artists by exact name match."""
        statement = select(Artist).where(Artist.Name == name)
        return list(self.session.scalars(statement))
    
    def find_by_name_pattern(self, pattern: str) -> list[Artist]:
        """Find artists by name pattern (LIKE)."""
        statement = select(Artist).where(Artist.Name.like(f"%{pattern}%"))
        return list(self.session.scalars(statement))
```

#### Asynchronous Custom Methods

```python
from sqlalchemy import select
from sqlrepository.async_repository import AsyncRepository

class AsyncArtistRepository(AsyncRepository[Artist, int]):
    async def find_by_name(self, name: str) -> list[Artist]:
        """Find artists by exact name match."""
        statement = select(Artist).where(Artist.Name == name)
        result = await self.session.scalars(statement)
        return list(result)
    
    async def find_by_name_pattern(self, pattern: str) -> list[Artist]:
        """Find artists by name pattern (LIKE)."""
        statement = select(Artist).where(Artist.Name.like(f"%{pattern}%"))
        result = await self.session.scalars(statement)
        return list(result)
```

**Key differences**:
- Methods are `async def`
- Use `await` for session operations
- Call `list()` on result after awaiting

## Testing Patterns

### Synchronous Tests

**Location**: `tests/test_repository.py`, `tests/test_sqlmodel_repository.py`

- **Database**: Session-scoped SQLite with pre-loaded Chinook database
- **Fixtures**: Defined in `tests/conftest.py`
- **Models**: Defined in `tests/models.py` (SQLAlchemy) and `tests/sqlmodel_models.py` (SQLModel)

Example:
```python
def test_find_by_id(artist_repo: ArtistRepository):
    """Test finding an entity by ID."""
    artist = artist_repo.find_by_id(1)
    assert artist is not None
    assert artist.Name == "AC/DC"
```

### Asynchronous Tests

**Location**: `tests/test_async_repository.py`, `tests/test_async_sqlmodel_repository.py`

- **Database**: Function-scoped in-memory SQLite (fresh per test)
- **Fixtures**: Use `@pytest_asyncio.fixture` decorator
- **Models**: Unique class names to avoid registry conflicts
  - `AsyncArtist`, `AsyncAlbum` (SQLAlchemy)
  - Shared SQLModel models from `tests/sqlmodel_models.py`

Example:
```python
@pytest.mark.asyncio
async def test_save_entity(async_session: AsyncSession):
    """Test saving an entity."""
    repo = ArtistRepository(async_session)
    artist = AsyncArtist(Name="Led Zeppelin")
    
    saved_artist = await repo.save(artist)
    await async_session.commit()
    
    assert saved_artist.ArtistId is not None
    assert saved_artist.Name == "Led Zeppelin"
```

**Important**: Use `expire_on_commit=False` in async session fixtures to prevent detached entity issues.

### Test Data

- **Sync tests**: Use pre-loaded Chinook database (Artists: AC/DC, Accept, Albums, etc.)
- **Async tests**: Load test data in fixtures (AC/DC, Accept as ArtistId 1 and 2)

## Dependencies

### Core Dependencies

```toml
[project]
dependencies = [
    "sqlalchemy (>=2.0.46,<3.0.0)"
]
```

### Optional Dependency Groups

```toml
[dependency-groups]
sqlmodel = [
    "sqlmodel (>=0.0.34,<0.1.0)"
]

async = [
    "aiosqlite (>=0.20.0,<0.21.0)",  # Async SQLite driver
    "greenlet (>=3.2.0,<4.0.0)"      # Required by SQLAlchemy async
]

dev = [
    "pytest (>=8.2.0,<9.0.0)",       # Downgraded for pytest-asyncio compatibility
    "pytest-coverage (>=0.0,<0.1)",
    "pytest-asyncio (>=0.26.0,<0.27.0)",
    "ruff (>=0.15.1,<0.16.0)",
    "mypy (>=1.19.1,<2.0.0)",
    { include-group = "sqlmodel" },
    { include-group = "async" }
]

gen = [
    "sqlacodegen (>=3.2.0,<4.0.0)"  # Optional: Generate models from existing databases
]
```

### Installation Examples

```bash
# Basic (SQLAlchemy only)
uv add sqlrepository

# With SQLModel support
uv add 'sqlrepository[sqlmodel]'

# With async support
uv add 'sqlrepository[async]'

# With everything
uv add 'sqlrepository[sqlmodel,async]'
```

## Code Conventions

### Style and Formatting

- **Line length**: 79 characters (enforced by Ruff)
- **Imports**: Organized with `ruff` (E, F, W, Q, I rules)
- **Formatting**: Use `ruff format` for consistent code style
- **Type hints**: Required for all public methods and function signatures

### Naming Conventions

- **Classes**: PascalCase (e.g., `ArtistRepository`, `AsyncRepository`)
- **Methods**: snake_case (e.g., `find_by_id`, `save_all`)
- **Private methods**: Prefix with `_` (e.g., `_model_type`)
- **Model attributes**: Use original database column names (e.g., `Artist.ArtistId`, `Artist.Name`)
- **Type variables**: 
  - `EntityType` for SQLAlchemy models (bound to `DeclarativeBase`)
  - `SQLModelEntityType` for SQLModel models (bound to `SQLModel`)
  - `IdType` for primary key types

### Docstrings

Following **Google style**:

```python
def find_by_id(self, id: IdType) -> EntityType | None:
    """
    Retrieves an entity by its id.

    Args:
        id (IdType): The identifier of the entity. Must not be None.

    Returns:
        EntityType | None: The entity with the given id, or None if not found.

    Raises:
        ValueError: If id is None.
    """
```

**Rules**:
- All public methods require docstrings
- Private methods (`_method`) only need docstrings if behavior is non-obvious
- Test functions should have brief docstrings explaining what they verify
- Class docstrings describe purpose and usage
- Module docstrings at the top of files

### Validation

- **None validation**: All repository methods validate that entities and IDs are not None
- Raise `ValueError` with descriptive message if None is passed

Example:
```python
if entity is None:
    raise ValueError("entity must not be None")
```

## Project Structure

```
sqlrepository/
├── .github/
│   ├── copilot-instructions.md      # Legacy instructions (being replaced)
│   ├── instructions.md               # This file
│   ├── copilot-skills/              # Reusable skills
│   │   ├── chore.instructions.md
│   │   └── release.instructions.md
│   └── workflows/
│       ├── build-wheels.yml         # Release workflow
│       └── ci.yml                   # CI workflow
├── src/sqlrepository/
│   ├── __init__.py                  # Package exports
│   ├── core.py                      # Sync: Repository, SQLModelRepository
│   └── async_repository.py          # Async: AsyncRepository, AsyncSQLModelRepository
├── tests/
│   ├── conftest.py                  # Test fixtures
│   ├── models.py                    # SQLAlchemy test models
│   ├── sqlmodel_models.py           # Shared SQLModel test models
│   ├── repositories.py              # Test repository implementations
│   ├── test_repository.py           # Sync SQLAlchemy tests (11 tests)
│   ├── test_sqlmodel_repository.py  # Sync SQLModel tests (12 tests)
│   ├── test_async_repository.py     # Async SQLAlchemy tests (19 tests)
│   └── test_async_sqlmodel_repository.py  # Async SQLModel tests (12 tests)
├── pyproject.toml                   # uv configuration, dependencies
├── uv.lock                          # Locked dependencies
├── README.md                        # User-facing documentation
└── LICENSE                          # GPL-3.0 license
```

## Common Tasks

### Adding a New Repository Method

1. **Decide sync vs async**: Add to `core.py` or `async_repository.py`
2. **Add to mixin**: Add to `_RepositoryMixin` or `_AsyncRepositoryMixin`
3. **Write docstring**: Follow Google style
4. **Add tests**: Test in both Repository and SQLModelRepository test files
5. **Run tests**: `uv run pytest -v`

### Adding a New Feature

1. **Create feature branch**: `git checkout -b feature/feature-name`
2. **Implement with tests**: TDD approach recommended
3. **Update README**: Add usage examples
4. **Run full test suite**: `uv run pytest -v`
5. **Check coverage**: `uv run pytest --cov`
6. **Lint and format**: `uv run ruff check . && uv run ruff format .`
7. **Commit**: Use conventional commits (feat:, fix:, docs:, etc.)

### Creating a Release

**The project now uses automated CI/CD for releases!**

1. **Update version**: Edit `pyproject.toml` (semantic versioning)
   ```toml
   [project]
   version = "0.2.0"  # Update this
   ```

2. **Commit and push**:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 0.2.0"
   git push
   ```

3. **Trigger release workflow**:
   - Go to GitHub Actions tab
   - Select "Release" workflow
   - Click "Run workflow"
   - Choose branch (usually `main`)
   - Click "Run workflow"

4. **Automated steps** (no manual intervention):
   - ✅ Extract version from pyproject.toml
   - ✅ Run quality checks (lint, format, mypy, tests)
   - ✅ Build package (wheel + sdist)
   - ✅ Create git tag (e.g., `v0.2.0`)
   - ✅ Create GitHub release with notes
   - ✅ Publish to PyPI

See [`.github/CICD.md`](.github/CICD.md) for detailed CI/CD documentation.

### Running Type Checks

```bash
# Check types in source
uv run mypy src/sqlrepository

# Check types in tests (may have issues due to test fixtures)
uv run mypy tests
```

## Important Notes

### Why Separate Repository Classes?

Initially, we tried using `Union[DeclarativeBase, SQLModel]` with conditional TYPE_CHECKING, but this created type system issues:
- SQLModel doesn't inherit from DeclarativeBase
- Mypy complained about TypeVar redefinition
- Pylance couldn't properly infer types

**Solution**: Separate classes with shared mixin implementation.
- **Benefit**: Clean, simple type definitions
- **Trade-off**: SQLModel users must use `SQLModelRepository` instead of `Repository`
- **Result**: Better type safety and IDE autocomplete

### Pytest Version Constraint

We use **pytest 8.x** instead of 9.x because:
- `pytest-asyncio 0.26.0` requires `pytest <9`
- This is a temporary constraint until pytest-asyncio adds pytest 9 support

### Async Session Best Practice

Always use `expire_on_commit=False` with async sessions:

```python
async with AsyncSession(engine, expire_on_commit=False) as session:
    repo = ArtistRepository(session)
    artist = await repo.save(Artist(Name="Test"))
    await session.commit()
    # Can still access artist.ArtistId without lazy-load errors
```

Without this, accessing entity attributes after commit triggers lazy loads that fail in async context.

## Versioning

- **Current version**: 0.1.8
- **Strategy**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Status**: Pre-1.0 (breaking changes allowed between minor versions)
- **Tags**: Format `vX.Y.Z` (e.g., `v0.1.8`)

## License

GPL-3.0 - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Run linters and formatters
6. Submit a pull request with clear description

For infrastructure changes (CI, build, etc.), use the `chore:` commit prefix.
For new features, use `feat:`.
For bug fixes, use `fix:`.
For documentation, use `docs:`.
