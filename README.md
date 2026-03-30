# sqlrepository

A Python repository pattern implementation for SQLAlchemy and SQLModel, inspired by Spring Data's JPA Repositories.

## Overview

`sqlrepository` provides a clean, type-safe repository pattern for database operations, eliminating boilerplate CRUD code and promoting consistent data access patterns across your application. Whether you're using SQLAlchemy's `DeclarativeBase` or SQLModel's enhanced models with validation, this library offers a unified interface for your data access layer.

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
uv add sqlrepository                       # SQLAlchemy only
uv add 'sqlrepository[sqlmodel]'           # + SQLModel support
uv add 'sqlrepository[async]'             # + async support
uv add 'sqlrepository[async,sqlmodel]'    # everything
```

`pip install` works the same way for non-uv projects.

## Usage

### SQLAlchemy

Define your models using SQLAlchemy's `DeclarativeBase` and create a repository by subclassing `Repository[ModelType, IdType]`:

```python
from enum import StrEnum
from sqlalchemy import Boolean, Integer, NVARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlrepository import Repository


class Base(DeclarativeBase): ...


class Genre(StrEnum):
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    OTHER = "other"


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(NVARCHAR(120))
    genre: Mapped[Genre] = mapped_column(default=Genre.OTHER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ArtistRepository(Repository[Artist, int]):
    pass
```

Then use it with a session:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///music.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    repo = ArtistRepository(session)

    # Create
    artist = Artist(name="Jimi Hendrix", genre=Genre.ROCK, is_active=False)
    repo.save(artist)
    session.commit()

    # Read
    found = repo.find_by_id(artist.id)
    all_artists = repo.find_all()

    # Update
    found.is_active = True
    repo.save(found)
    session.commit()

    # Delete
    repo.delete_by_id(artist.id)
    session.commit()
```

### SQLModel

SQLModel combines SQLAlchemy's power with Pydantic's validation. Import `Repository` from `sqlrepository.sqlmodel`. The `Genre` enum is the same as in the SQLAlchemy example.

```python
from sqlmodel import Field, SQLModel
from sqlrepository.sqlmodel import Repository


class Artist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, max_length=120)
    genre: Genre | None = Field(default=Genre.OTHER)
    is_active: bool = Field(default=True)


class ArtistRepository(Repository[Artist, int]):
    pass
```

Then use it with a session:

```python
from sqlmodel import create_engine, Session, SQLModel

engine = create_engine("sqlite:///music.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    repo = ArtistRepository(session)

    # Bulk create
    artists = [
        Artist(name="Jimi Hendrix", genre=Genre.ROCK),
        Artist(name="Amy Winehouse", genre=Genre.JAZZ),
        Artist(name="The Weeknd", genre=Genre.POP, is_active=True),
    ]
    repo.save_all(artists)
    session.commit()

    print(repo.count())           # 3
    print(repo.exists_by_id(1))   # True
```

### Async Repositories

For async applications, use `AsyncRepository` with SQLAlchemy's `AsyncSession`. Always set `expire_on_commit=False` on the session to avoid lazy-loading errors after commit.

#### SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository import AsyncRepository


class ArtistRepository(AsyncRepository[Artist, int]):
    pass


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///music.db")

    async with AsyncSession(engine, expire_on_commit=False) as session:
        repo = ArtistRepository(session)

        artist = Artist(name="Herbie Hancock", genre=Genre.JAZZ, is_active=True)
        await repo.save(artist)
        await session.commit()

        all_artists = await repo.find_all()
        count = await repo.count()
        await repo.delete_by_id(artist.id)
        await session.commit()
```

#### SQLModel

The pattern is identical — just import `AsyncRepository` from `sqlrepository.sqlmodel` instead:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlrepository.sqlmodel import AsyncRepository


class ArtistRepository(AsyncRepository[Artist, int]):
    pass
```

### Transaction Management

Repositories never commit, rollback, or expose transaction control — that responsibility belongs to the caller. The recommended pattern is to use the session as a context manager, which handles commit and rollback automatically:

```python
# Sync — multiple repositories in one transaction
with Session(engine) as session:
    artist_repo = ArtistRepository(session)
    album_repo = AlbumRepository(session)

    artist = Artist(name="Nirvana", genre=Genre.ROCK)
    artist_repo.save(artist)

    album = Album(title="Nevermind", artist_id=artist.id)
    album_repo.save(album)

    session.commit()  # both committed together, or neither on exception
```

```python
# Async — same pattern with await
async with AsyncSession(engine, expire_on_commit=False) as session:
    artist_repo = ArtistRepository(session)
    album_repo = AlbumRepository(session)

    artist = Artist(name="Amy Winehouse", genre=Genre.JAZZ)
    await artist_repo.save(artist)

    album = Album(title="Back to Black", artist_id=artist.id)
    await album_repo.save(album)

    await session.commit()  # both committed together, or neither on exception
```

## Available Methods

All repository classes expose the same interface out of the box. Async variants are `async def` and must be `await`ed.

| Method | Returns | Notes |
|---|---|---|
| `save(entity)` | `EntityType` | Insert or merge; flushes to populate generated IDs |
| `save_all(entities)` | `Sequence[EntityType]` | Save a collection |
| `find_by_id(id)` | `EntityType \| None` | |
| `find_all(order_by=None)` | `Sequence[EntityType]` | Optionally pass a column expression to order results |
| `find_all_by_id(ids)` | `Sequence[EntityType]` | Efficient batch lookup for a known set of IDs |
| `exists_by_id(id)` | `bool` | |
| `count()` | `int` | |
| `delete(entity)` | `None` | |
| `delete_by_id(id)` | `None` | |
| `delete_all(entities=None)` | `None` | Pass `None` to delete **all rows** in the table |
| `delete_all_by_id(ids)` | `None` | |

## Adding Custom Query Methods

Extend the repository class with your own query methods using `self.session`:

```python
from sqlalchemy import select
from sqlrepository import Repository


class ArtistRepository(Repository[Artist, int]):
    def find_by_genre(self, genre: Genre) -> list[Artist]:
        """Find all artists in a given genre."""
        stmt = select(Artist).where(Artist.genre == genre)
        return list(self.session.scalars(stmt))

    def find_active(self) -> list[Artist]:
        """Find all active artists."""
        stmt = select(Artist).where(Artist.is_active.is_(True))
        return list(self.session.scalars(stmt))
```

For async repositories, use the same pattern with `async def` and `await self.session.scalars(...)`.

## Contributing

### Setting Up

```bash
git clone https://github.com/cstotzer/sqlrepository.git
cd sqlrepository
uv sync --all-groups
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=sqlrepository --cov-report=term-missing

# One suite only
uv run pytest tests/sqlalchemy -v
uv run pytest tests/sqlmodel -v
```

### Code Quality

```bash
uv run ruff check src tests       # lint
uv run ruff format src tests      # format
uv run pyright src                # type check
```

### Submitting Changes

1. Fork the repository and create a branch from `main`
2. Make your changes with clear, conventional commit messages
3. Ensure all tests pass and code is properly formatted
4. Open a Pull Request — CI will run lint, type checks, security scan, and tests on Python 3.11–3.14

### Release Process

Push a tag — the version is derived from it at build time via `hatch-vcs`, and the release workflow triggers automatically:

```bash
git tag vX.Y.Z
git push origin main vX.Y.Z
```

The workflow runs the quality gate, builds the package, publishes a GitHub release with generated release notes, and uploads to PyPI — all without further intervention.

> **Dry run**: trigger `release.yml` manually via `workflow_dispatch` with `dry_run: true` to validate the quality gate and build without publishing.

## License

This project is licensed under the **GNU General Public License v3.0**.

- ✅ **Free to use** — commercially or personally
- ✅ **Modify and distribute** — make changes and share
- ⚠️ **Share alike** — derivative works must use GPL-3.0
- ⚠️ **Disclose source** — source code must be available

See the [LICENSE](LICENSE) file for the full license text.

---

**Made with ❤️ by the sqlrepository contributors**
