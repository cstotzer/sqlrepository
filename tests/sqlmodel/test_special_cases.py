"""Provides tests for special cases of the SQLAlchemy repository."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from sqlmodel import Field, Session, SQLModel, create_engine

from sqlrepository.sqlmodel import Repository
from tests.sqlmodel.models import Album, Artist
from tests.sqlmodel.repositories import ArtistRepository


class CompositeEntity(SQLModel, table=True):
    id1: int | None = Field(default=None, primary_key=True)
    id2: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, max_length=120)


MyIdType = tuple[int, int]


@pytest.fixture(autouse=True)
def session(
    test_data: tuple[list[dict], list[dict]],
) -> Generator[Session, None, None]:
    """Fixture for creating a SQLAlchemy session with in-memory SQLite database."""  # noqa: E501

    engine = create_engine("sqlite:///:memory:", echo=True)

    SQLModel.metadata.create_all(engine)

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
    SQLModel.metadata.create_all(engine)
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


def test_exists_by_id_composite_pk(session: Session) -> None:
    """exists_by_id handles the composite-PK path correctly."""

    class CompositeRepo(Repository[CompositeEntity, tuple]): ...

    repo = CompositeRepo(session)
    assert repo.exists_by_id((1, 2)) is True
    assert repo.exists_by_id((9, 9)) is False


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
