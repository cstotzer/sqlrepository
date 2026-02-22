# sqlrepository

A Python repository pattern implementation for SQLAlchemy and SQLModel, inspired by Spring Data's JPA Repositories.

## Overview

`sqlrepository` provides a clean, type-safe repository pattern for database operations, eliminating boilerplate CRUD code and promoting consistent data access patterns across your application. Whether you're using SQLAlchemy's `DeclarativeBase` or SQLModel's enhanced models with validation, this library offers a unified interface for your data access layer.

**Inspired by Spring Data JPA**, this package brings the elegant repository pattern from the Java ecosystem to Python, adapted for SQLAlchemy's powerful ORM capabilities.

### Key Features

- 🎯 **Type-safe** - Full type hints and generic support for IDE autocomplete
- 🔄 **Dual ORM support** - Works with both SQLAlchemy and SQLModel
- ⚡ **Async support** - First-class async/await support with AsyncRepository
- 🚀 **Zero boilerplate** - Common CRUD operations out of the box
- 🧩 **Extensible** - Easy to add custom query methods
- ✅ **Well-tested** - Comprehensive test suite with high coverage
- 📦 **Lightweight** - Minimal dependencies

## Installation

```bash
# Basic installation with SQLAlchemy support
pip install sqlrepository

# Or with uv
uv add sqlrepository

# For SQLModel support (optional)
pip install 'sqlrepository[sqlmodel]'
# or with uv
uv add 'sqlrepository[sqlmodel]'

# For async support (SQLAlchemy async)
pip install 'sqlrepository[async]'
# or with uv
uv add 'sqlrepository[async]'

# For full async + SQLModel support
pip install 'sqlrepository[async,sqlmodel]'
# or with uv
uv add 'sqlrepository[async,sqlmodel]'
```

## Usage

### Creating Repositories with SQLAlchemy

Define your model using SQLAlchemy's `DeclarativeBase`:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlrepository import Base, Repository


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)


class UserRepository(Repository[User, int]):
    """Repository for User model."""
    pass
```

Use the repository in your application:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Setup
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user_repo = UserRepository(session)
    
    # Create
    new_user = User(username="john_doe", email="john@example.com", age=30)
    user_repo.save(new_user)
    session.commit()
    
    # Read
    user = user_repo.find_by_id(1)
    all_users = user_repo.find_all()
    
    # Update
    user.email = "newemail@example.com"
    user_repo.save(user)
    session.commit()
    
    # Delete
    user_repo.delete_by_id(1)
    session.commit()
    
    # Count
    total = user_repo.count()
```

### Creating Repositories with SQLModel

SQLModel combines SQLAlchemy's power with Pydantic's validation:

```python
from sqlmodel import Field, SQLModel
from sqlrepository import SQLModelRepository


class Artist(SQLModel, table=True):
    """SQLModel artist with built-in validation."""
    __tablename__ = "artists"
    
    ArtistId: int | None = Field(default=None, primary_key=True)
    Name: str = Field(index=True, min_length=1, max_length=120)


class ArtistRepository(SQLModelRepository[Artist, int]):
    """Repository for Artist model."""
    pass
```

Use with SQLModel:

```python
from sqlmodel import create_engine, Session, SQLModel

# Setup
engine = create_engine("sqlite:///music.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    artist_repo = ArtistRepository(session)
    
    # Create with validation
    artist = Artist(Name="AC/DC")
    artist_repo.save(artist)
    session.commit()
    
    # Bulk operations
    artists = [
        Artist(Name="Led Zeppelin"),
        Artist(Name="Pink Floyd"),
    ]
    artist_repo.save_all(artists)
    session.commit()
```

### Using Async Repositories

For asynchronous database operations, use `AsyncRepository` with SQLAlchemy's async capabilities:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository import Base
from sqlrepository.async_repository import AsyncRepository

class Artist(Base):
    __tablename__ = "artists"
    
    ArtistId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(String(120))


class ArtistRepository(AsyncRepository[Artist, int]):
    pass


# Usage
async def main():
    engine = create_async_engine("sqlite+aiosqlite:///music.db")
    
    async with AsyncSession(engine) as session:
        artist_repo = ArtistRepository(session)
        
        # All repository methods are async
        artist = Artist(Name="AC/DC")
        await artist_repo.save(artist)
        await session.commit()
        
        # Find operations
        found = await artist_repo.find_by_id(1)
        all_artists = await artist_repo.find_all()
        count = await artist_repo.count()
        
        # Delete operations
        await artist_repo.delete_by_id(1)
        await session.commit()
```

SQLModel also supports async operations:

```python
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository.async_repository import AsyncSQLModelRepository

class Artist(SQLModel, table=True):
    __tablename__ = "artists"
    
    ArtistId: int | None = Field(default=None, primary_key=True)
    Name: str = Field(max_length=120)


class ArtistRepository(AsyncSQLModelRepository[Artist, int]):
    pass


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///music.db")
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        artist_repo = ArtistRepository(session)
        
        artist = Artist(Name="Led Zeppelin")
        await artist_repo.save(artist)
        await session.commit()
```

**Note**: When using async sessions, set `expire_on_commit=False` to avoid lazy-loading issues after commit.

## Transaction Management

Following the Spring Data JPA pattern, repositories do **not** expose transaction control methods (`commit()`, `flush()`, `rollback()`). Transaction boundaries should be managed by the caller (e.g., service layer or application code).

### Why This Pattern?

This separation of concerns provides several benefits:
- **Clear Responsibility**: Repositories handle data access, not transaction boundaries
- **Flexibility**: The caller controls when to commit or rollback
- **Composability**: Multiple repository calls can participate in a single transaction
- **Testability**: Easier to test with controlled transaction boundaries

### Synchronous Transaction Management

#### Using Context Managers (Recommended)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlrepository import Repository

engine = create_engine("sqlite:///chinook.db")

# Context manager handles commit/rollback automatically
with Session(engine) as session:
    repo = Repository[Artist, int](Artist, session)
    
    artist = Artist(Name="Pink Floyd")
    repo.save(artist)
    
    # Commit happens automatically when exiting the context
    # Rollback happens automatically on exception

# For multiple operations in one transaction:
with Session(engine) as session:
    artist_repo = Repository[Artist, int](Artist, session)
    album_repo = Repository[Album, int](Album, session)
    
    artist = Artist(Name="The Beatles")
    artist_repo.save(artist)
    
    album = Album(Title="Abbey Road", ArtistId=artist.ArtistId)
    album_repo.save(album)
    
    # Both operations committed together
```

#### Manual Transaction Control

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlrepository import Repository

engine = create_engine("sqlite:///chinook.db")

session = Session(engine)
try:
    repo = Repository[Artist, int](Artist, session)
    
    artist = Artist(Name="Queen")
    repo.save(artist)
    
    # Explicitly commit
    session.commit()
except Exception as e:
    # Explicitly rollback on error
    session.rollback()
    raise
finally:
    session.close()
```

### Asynchronous Transaction Management

#### Using Async Context Managers (Recommended)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository import AsyncRepository

engine = create_async_engine("sqlite+aiosqlite:///:memory:")

# Context manager handles commit/rollback automatically
async with AsyncSession(engine, expire_on_commit=False) as session:
    repo = AsyncRepository[AsyncArtist, int](AsyncArtist, session)
    
    artist = AsyncArtist(Name="Radiohead")
    await repo.save(artist)
    
    # Commit happens automatically when exiting the context
    # Rollback happens automatically on exception

# For multiple operations in one transaction:
async with AsyncSession(engine, expire_on_commit=False) as session:
    artist_repo = AsyncRepository[AsyncArtist, int](AsyncArtist, session)
    album_repo = AsyncRepository[AsyncAlbum, int](AsyncAlbum, session)
    
    artist = AsyncArtist(Name="Nirvana")
    await artist_repo.save(artist)
    
    album = AsyncAlbum(Title="Nevermind", ArtistId=artist.ArtistId)
    await album_repo.save(album)
    
    # Both operations committed together
```

#### Manual Async Transaction Control

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository import AsyncRepository

engine = create_async_engine("sqlite+aiosqlite:///:memory:")

session = AsyncSession(engine, expire_on_commit=False)
try:
    repo = AsyncRepository[AsyncArtist, int](AsyncArtist, session)
    
    artist = AsyncArtist(Name="Metallica")
    await repo.save(artist)
    
    # Explicitly commit
    await session.commit()
except Exception as e:
    # Explicitly rollback on error
    await session.rollback()
    raise
finally:
    await session.close()
```

### Best Practices

1. **Use Context Managers**: They automatically handle commit/rollback and cleanup
2. **One Transaction per Use Case**: Group related operations in a single transaction
3. **Handle Errors Gracefully**: Always rollback on exceptions
4. **Set expire_on_commit=False**: For async sessions to avoid lazy-loading issues
5. **Service Layer Pattern**: Let services manage transactions, repositories manage data

### Adding Custom Query Methods

Extend the repository with your own query methods:

```python
from sqlalchemy import select
from sqlrepository import Repository


class UserRepository(Repository[User, int]):
    def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        statement = select(User).where(User.username == username)
        return self.session.scalar(statement)
    
    def find_by_age_range(self, min_age: int, max_age: int) -> list[User]:
        """Find users within age range."""
        statement = (
            select(User)
            .where(User.age >= min_age, User.age <= max_age)
            .order_by(User.age)
        )
        return list(self.session.scalars(statement))
    
    def find_active_users(self) -> list[User]:
        """Custom business logic query."""
        statement = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.username)
        )
        return list(self.session.scalars(statement))
```

For async repositories, use the same pattern with async methods:

```python
from sqlalchemy import select
from sqlrepository.async_repository import AsyncRepository


class AsyncUserRepository(AsyncRepository[User, int]):
    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        statement = select(User).where(User.username == username)
        result = await self.session.scalar(statement)
        return result
    
    async def find_by_age_range(self, min_age: int, max_age: int) -> list[User]:
        """Find users within age range."""
        statement = (
            select(User)
            .where(User.age >= min_age, User.age <= max_age)
            .order_by(User.age)
        )
        result = await self.session.scalars(statement)
        return list(result)
    
    async def find_active_users(self) -> list[User]:
        """Custom business logic query."""
        statement = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.username)
        )
        result = await self.session.scalars(statement)
        return list(result)


# Usage
async def main():
    async with AsyncSession(engine) as session:
        user_repo = AsyncUserRepository(session)
        
        # Use custom async methods
        user = await user_repo.find_by_username("john_doe")
        active_users = await user_repo.find_active_users()
        young_users = await user_repo.find_by_age_range(18, 30)
```
```

### Available Repository Methods

All repositories provide these methods out of the box:

**Create/Update:**
- `save(entity)` - Save or update a single entity
- `save_all(entities)` - Save or update multiple entities

**Read:**
- `find_by_id(id)` - Find entity by primary key
- `find_all()` - Get all entities
- `find_all_by_id(ids)` - Find multiple entities by IDs
- `exists_by_id(id)` - Check if entity exists
- `count()` - Count total entities

**Delete:**
- `delete(entity)` - Delete a single entity
- `delete_by_id(id)` - Delete by primary key
- `delete_all()` - Delete all entities
- `delete_all_by_id(ids)` - Delete multiple by IDs

**Transaction Control:**
- `flush()` - Flush pending changes
- `commit()` - Commit transaction
- `rollback()` - Rollback transaction

## Contributing

We welcome contributions! Here's how to get started:

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/cstotzer/sqlrepository.git
cd sqlrepository

# Install dependencies with uv
uv sync --all-groups

# The virtual environment is automatically managed by uv
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sqlrepository --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_repository.py -v

# Run specific test
uv run pytest tests/test_repository.py::test_save -v

# Run async tests only
uv run pytest tests/test_async_repository.py tests/test_async_sqlmodel_repository.py -v
```

### Code Quality Checks

```bash
# Run linter
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check --fix src tests

# Format code
uv run ruff format src tests

# Type checking
uv run mypy src/sqlrepository --ignore-missing-imports
```

### Submitting Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, descriptive commits
4. **Ensure all tests pass** and code is properly formatted
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Test coverage for new features

### Pull Request Guidelines

- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation if needed
- Keep changes focused and atomic
- Ensure CI checks pass before requesting review

All pull requests trigger automated checks:
- ✅ Linting (ruff)
- ✅ Type checking (mypy)
- ✅ Security scanning (pip-audit)
- ✅ Tests on Python 3.11 & 3.12
- ✅ Coverage reporting

### Release Process

Releases are fully automated via GitHub Actions. See [CI/CD Documentation](.github/CICD.md) for details.

**Quick release steps**:
1. Update version in `pyproject.toml`
2. Commit: `git commit -m "chore: bump version to X.Y.Z"`
3. Push to GitHub
4. Go to Actions → Release workflow → Run workflow
5. Package is automatically built, tagged, and published to PyPI

For detailed instructions, see [`.github/CICD.md`](.github/CICD.md).

## License

This project is licensed under the **GNU General Public License v3.0**.

### What This Means

- ✅ **Free to use** - Use commercially or personally
- ✅ **Modify and distribute** - Make changes and share
- ⚠️ **Share alike** - Derivative works must use GPL-3.0
- ⚠️ **Disclose source** - Source code must be available
- ⚠️ **Include license** - Copy of GPL-3.0 must be included

See the [LICENSE](LICENSE) file for the full license text.

### Why GPL-3.0?

We believe in open source software and want to ensure that improvements to this library remain open and available to everyone. The GPL-3.0 license guarantees that all derivatives and modifications stay free and open source.

---

**Made with ❤️ by the sqlrepository contributors**
