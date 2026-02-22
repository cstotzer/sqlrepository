from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import Session, SQLModel, create_engine

from tests.sqlmodel.models import Album, Artist
from tests.sqlmodel.repositories import ArtistRepository, AsyncArtistRepository


@pytest.fixture(autouse=True)
def session(
    test_data: tuple[list[dict], list[dict]],
) -> Generator[Session, None, None]:
    """Fixture for creating a SQLAlchemy session with in-memory SQLite database."""  # noqa: E501

    engine = create_engine("sqlite:///:memory:", echo=True)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for artist_data in test_data[0]:
            artist = Artist(**artist_data)
            session.add(artist)

        for album_data in test_data[1]:
            album = Album(**album_data)
            session.add(album)

        session.commit()

        yield session

    session.close()


@pytest.fixture(autouse=True)
def artist_repository(session: Session) -> ArtistRepository:
    return ArtistRepository(session)


@pytest_asyncio.fixture(autouse=True)
async def async_session(
    test_data: tuple[list[dict], list[dict]],
) -> AsyncGenerator[AsyncSession, None]:
    """Fixture for creating an async SQLAlchemy session with in-memory SQLite database."""  # noqa: E501

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # expire_on_commit=False will prevent attributes from being expired
    # after commit.
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        for artist_data in test_data[0]:
            artist = Artist(**artist_data)
            session.add(artist)

        for album_data in test_data[1]:
            album = Album(**album_data)
            session.add(album)

        await session.commit()

        yield session

    await session.close()
    await engine.dispose()


@pytest.fixture
def async_artist_repository(
    async_session: AsyncSession,
) -> AsyncArtistRepository:
    return AsyncArtistRepository(async_session)
