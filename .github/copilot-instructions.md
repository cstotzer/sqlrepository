# sqla-repository

A SQLAlchemy repository implementation inspired by Spring Data JPA repositories.

**Note**: This file is deprecated. Please refer to `.github/instructions.md` for up-to-date project documentation.

## Build, Test, and Lint

This project uses **uv** for dependency management.

```bash
# Install dependencies
uv sync --all-groups

# Run all tests
uv run pytest

# Run a specific test
uv run pytest tests/test_repository.py::test_find_by_id

# Run tests with coverage
uv run pytest --cov=sqla_repository

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

## Architecture

### Core Pattern: Generic Repository

The `Repository[EntityType, IdType]` class in `src/sqla_repository/core.py` provides CRUD operations for SQLAlchemy models through Python generics. Key implementation details:

- **Type inference**: The `__init_subclass__` method automatically extracts the model type from generic parameters (e.g., `Repository[Artist, int]` sets `cls.model = Artist`)
- **Base class requirement**: All models must inherit from `sqla_repository.core.Base` (which extends `DeclarativeBase`)
- **Session management**: Repositories receive a `Session` in `__init__` and use it for all database operations
- **Transaction control**: The repository provides `flush()`, `commit()`, and `rollback()` methods, but operations like `save()` only flush by default—commit is the caller's responsibility

### Custom Repository Methods

To add custom queries, extend `Repository` and use `self._model_type()` to get the model class and `self.session` for queries:

```python
class ArtistRepository(Repository[Artist, int]):
    def find_by_name(self, name: str) -> list[Artist]:
        return self.session.query(self._model_type()).filter_by(Name=name).all()
```

### Test Setup Pattern

Tests use a session-scoped SQLite in-memory database loaded from `tests/resources/chinook.db`. Repository fixtures are session-scoped and share the same database connection. See `tests/conftest.py` for the fixture setup.

## Conventions

- **Line length**: 79 characters (enforced by Ruff)
- **None validation**: Repository methods validate that entities and IDs are not None, raising `ValueError` if violated
- **Model generation**: The optional `gen` dependency group includes `sqlacodegen` for generating model classes from existing databases
- **Naming**: Models use PascalCase with their original database column names (e.g., `Artist.ArtistId`, `Artist.Name`)
- **Docstrings**: 
    - Docstrings are to be written in English and follow the Google style guide.
    - All public methods have docstrings describing their behavior and parameters
    - Private methods (those starting with an underscore) do not require docstrings unless their behavior is non-obvious
    - Class docstrings describe the purpose of the class and any important implementation details or usage notes
    - Modules should have a docstring at the top describing their contents and any important context for users
    - Docstrings should be concise but informative, providing enough context for users to understand the method's purpose and how to use it without needing to read the implementation details
    - Tests should have docstrings describing the purpose of the test and what behavior it is verifying, especially for more complex test cases
- **Versioning**: The project follows semantic versioning, with the version number updated in `pyproject.toml` for each release. The current version is 0.1.2, indicating that the project is in early development and may have breaking changes before reaching 1.0.0. Version tags should be created in Git for each release, following the format `vX.Y.Z` (e.g., `v0.1.2`). 