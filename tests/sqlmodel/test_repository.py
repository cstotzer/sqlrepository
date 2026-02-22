"""Tests for synchronous Repository with SQLAlchemy models."""

import pytest
from sqlmodel import Session

from tests.sqlmodel.models import Artist, Genre
from tests.sqlmodel.repositories import ArtistRepository


def test_count(artist_repository: ArtistRepository) -> None:
    assert artist_repository.count() == 6


def test_find_all(artist_repository: ArtistRepository) -> None:
    assert len(artist_repository.find_all()) == 6


def test_find_by_id(artist_repository: ArtistRepository) -> None:
    artist = artist_repository.find_by_id(1)
    assert artist is not None
    assert artist.id == 1
    assert artist.name == "Jimi Hendrix"


def test_find_by_id_not_found(artist_repository: ArtistRepository) -> None:
    assert artist_repository.find_by_id(9999) is None


def test_find_by_id_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        artist_repository.find_by_id(None)  # type: ignore[arg-type]


def test_exists_by_id(artist_repository: ArtistRepository) -> None:
    assert artist_repository.exists_by_id(1) is True
    assert artist_repository.exists_by_id(9999) is False


def test_exists_by_id_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        artist_repository.exists_by_id(None)  # type: ignore[arg-type]


def test_find_all_by_id(artist_repository: ArtistRepository) -> None:
    artists = artist_repository.find_all_by_id([1, 3, 6, 9999])
    assert len(artists) == 3
    names = {a.name for a in artists}
    assert names == {"Jimi Hendrix", "Amy Winehouse", "Herbie Hancock"}


def test_find_all_by_id_none_raises(
    artist_repository: ArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="ids must not contain None"):
        artist_repository.find_all_by_id([1, None])  # type: ignore[list-item]


def test_save(artist_repository: ArtistRepository, session: Session) -> None:
    new_artist = Artist(name="Sleep Token", genre=Genre.ROCK, is_active=True)
    saved = artist_repository.save(new_artist)
    session.commit()

    assert saved.id is not None
    found = artist_repository.find_by_id(saved.id)
    assert found is not None
    assert found.name == "Sleep Token"
    assert artist_repository.count() == 7


def test_save_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="entity must not be None"):
        artist_repository.save(None)  # type: ignore[arg-type]


def test_save_all(
    artist_repository: ArtistRepository, session: Session
) -> None:
    new_artists = [
        Artist(name="Sleep Token", genre=Genre.ROCK, is_active=True),
        Artist(name="Spiritbox", genre=Genre.METAL, is_active=True),
    ]
    saved = artist_repository.save_all(new_artists)
    session.commit()

    assert len(saved) == 2
    assert all(a.id is not None for a in saved)
    assert artist_repository.count() == 8


def test_save_all_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="entities must not contain None"):
        artist_repository.save_all([Artist(name="Valid"), None])  # type: ignore[list-item]


def test_delete(artist_repository: ArtistRepository, session: Session) -> None:
    artist = artist_repository.find_by_id(6)
    assert artist is not None
    artist_repository.delete(artist)
    session.commit()

    assert artist_repository.find_by_id(6) is None
    assert artist_repository.count() == 5


def test_delete_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="entity must not be None"):
        artist_repository.delete(None)  # type: ignore[arg-type]


def test_delete_by_id(
    artist_repository: ArtistRepository, session: Session
) -> None:
    artist_repository.delete_by_id(6)
    session.commit()

    assert artist_repository.find_by_id(6) is None
    assert artist_repository.count() == 5


def test_delete_by_id_not_found(
    artist_repository: ArtistRepository, session: Session
) -> None:
    artist_repository.delete_by_id(9999)
    session.commit()

    assert artist_repository.count() == 6


def test_delete_by_id_none_raises(artist_repository: ArtistRepository) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        artist_repository.delete_by_id(None)  # type: ignore[arg-type]


def test_delete_all_by_id(
    artist_repository: ArtistRepository, session: Session
) -> None:
    artist_repository.delete_all_by_id([1, 2, 3])
    session.commit()

    assert artist_repository.count() == 3


def test_delete_all_by_id_none_raises(
    artist_repository: ArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="ids must not contain None"):
        artist_repository.delete_all_by_id([1, None])  # type: ignore[list-item]


def test_delete_all(
    artist_repository: ArtistRepository, session: Session
) -> None:
    artist_repository.delete_all()
    session.commit()

    assert artist_repository.count() == 0


def test_delete_all_with_entities(
    artist_repository: ArtistRepository, session: Session
) -> None:
    artists = artist_repository.find_all()
    artist_repository.delete_all(artists)
    session.commit()

    assert artist_repository.count() == 0


def test_delete_all_entities_none_raises(
    artist_repository: ArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="entities must not contain None"):
        artist_repository.delete_all([None])  # type: ignore[list-item]


def test_find_by_name(artist_repository: ArtistRepository) -> None:
    artists = artist_repository.find_by_name("Amy Winehouse")
    assert len(artists) == 1
    assert artists[0].id == 3
