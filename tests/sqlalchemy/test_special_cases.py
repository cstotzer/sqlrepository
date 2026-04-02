"""Provides tests for special cases of the SQLAlchemy repository."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import Integer, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from sqlrepository import AsyncRepository, Repository
from tests.sqlalchemy.models import Album, Artist
from tests.sqlalchemy.models import Base as ModelBase
from tests.sqlalchemy.repositories import ArtistRepository


class Base(DeclarativeBase): ...


class CompositeEntity(Base):
    __tablename__ = "composite_entity"

    id1: Mapped[int] = mapped_column(Integer, primary_key=True)
    id2: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column()


MyIdType = tuple[int, int]


@pytest.fixture(autouse=True)
def session(
    test_data: tuple[list[dict], list[dict]],
) -> Generator[Session, None, None]:
    """Fixture for creating a SQLAlchemy session with in-memory SQLite database."""  # noqa: E501

    engine = create_engine("sqlite:///:memory:", echo=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        entity = CompositeEntity(id1=1, id2=2, name="Test Entity")
        session.add(entity)
        session.commit()

        yield session

    session.close()


@pytest.fixture
def artist_session(
    test_data: tuple[list[dict], list[dict]],
) -> Generator[Session, None, None]:
    """Session fixture with Artist/Album data for identity-map tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    ModelBase.metadata.create_all(engine)
    with Session(engine) as session:
        for artist_data in test_data[0]:
            session.add(Artist(**artist_data))
        for album_data in test_data[1]:
            session.add(Album(**album_data))
        session.commit()
        yield session
    session.close()


def test_exists_by_id_does_not_load_entity(
    artist_session: Session,
) -> None:
    """exists_by_id must not call session.get() (no full entity load)."""
    repo = ArtistRepository(artist_session)
    with patch.object(artist_session, "get") as mock_get:
        result = repo.exists_by_id(1)
        assert result is True
        mock_get.assert_not_called()


@pytest_asyncio.fixture
async def async_composite_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session fixture with CompositeEntity data."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        session.add(CompositeEntity(id1=1, id2=2, name="Test Entity"))
        await session.commit()
        yield session
    await engine.dispose()


def test_exists_by_id_composite_pk(session: Session) -> None:
    """exists_by_id handles the composite-PK path correctly."""

    class CompositeRepo(Repository[CompositeEntity, tuple]): ...

    repo = CompositeRepo(session)
    assert repo.exists_by_id((1, 2)) is True
    assert repo.exists_by_id((9, 9)) is False


@pytest.mark.asyncio
async def test_exists_by_id_composite_pk_async(
    async_composite_session: AsyncSession,
) -> None:
    """exists_by_id async handles the composite-PK path correctly."""

    class CompositeAsyncRepo(AsyncRepository[CompositeEntity, tuple]): ...

    repo = CompositeAsyncRepo(async_composite_session)
    assert await repo.exists_by_id((1, 2)) is True
    assert await repo.exists_by_id((9, 9)) is False


def test_delete_by_id_composite_pk(session: Session) -> None:
    """delete_by_id handles the composite-PK path correctly."""

    class CompositeRepo(Repository[CompositeEntity, tuple]): ...

    repo = CompositeRepo(session)
    repo.delete_by_id((1, 2))
    session.commit()
    assert repo.find_by_id((1, 2)) is None


@pytest.mark.asyncio
async def test_delete_by_id_composite_pk_async(
    async_composite_session: AsyncSession,
) -> None:
    """delete_by_id async handles the composite-PK path correctly."""

    class CompositeAsyncRepo(AsyncRepository[CompositeEntity, tuple]): ...

    repo = CompositeAsyncRepo(async_composite_session)
    await repo.delete_by_id((1, 2))
    await async_composite_session.commit()
    assert await repo.find_by_id((1, 2)) is None


def test_composite_primary_key(session: Session) -> None:
    """Test that repositories can handle composite primary keys.

    We do not want to test the ORMs handling of composite primary keys, but
    we want to verify that the repository can be instantiated with a model
    that has a composite primary key without raising an error in
    __init_subclass__. This verifies that the repository does not assume that
    the primary key is a single column and does not raise an error when it
    encounters a model with a composite primary key and thus ensures that the
    capabilities of the ORM are not limited by the repository implementation.
    """

    class CompositeRepo(Repository[CompositeEntity, tuple]): ...

    repo = CompositeRepo(session)
    assert repo.model is CompositeEntity
    assert repo.find_by_id((1, 2)) is not None
