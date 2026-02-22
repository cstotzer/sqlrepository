"""Tests for asynchronous AsyncRepository with SQLAlchemy models."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.sqlmodel.models import Artist, Genre
from tests.sqlmodel.repositories import (
    AsyncArtistRepository,
)


@pytest.mark.asyncio
async def test_count(async_artist_repository: AsyncArtistRepository) -> None:
    assert await async_artist_repository.count() == 6


@pytest.mark.asyncio
async def test_find_all(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    assert len(await async_artist_repository.find_all()) == 6


@pytest.mark.asyncio
async def test_find_by_id(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    artist = await async_artist_repository.find_by_id(1)
    assert artist is not None
    assert artist.id == 1
    assert artist.name == "Jimi Hendrix"


@pytest.mark.asyncio
async def test_find_by_id_not_found(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    assert await async_artist_repository.find_by_id(9999) is None


@pytest.mark.asyncio
async def test_find_by_id_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        await async_artist_repository.find_by_id(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_exists_by_id(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    assert await async_artist_repository.exists_by_id(1) is True
    assert await async_artist_repository.exists_by_id(9999) is False


@pytest.mark.asyncio
async def test_exists_by_id_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        await async_artist_repository.exists_by_id(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_find_all_by_id(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    artists = await async_artist_repository.find_all_by_id([1, 3, 6, 9999])
    assert len(artists) == 3
    names = {a.name for a in artists}
    assert names == {"Jimi Hendrix", "Amy Winehouse", "Herbie Hancock"}


@pytest.mark.asyncio
async def test_find_all_by_id_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="ids must not contain None"):
        await async_artist_repository.find_all_by_id([1, None])  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_save(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    new_artist = Artist(name="Sleep Token", genre=Genre.ROCK, is_active=True)
    saved = await async_artist_repository.save(new_artist)
    await async_session.commit()

    assert saved.id is not None
    found = await async_artist_repository.find_by_id(saved.id)
    assert found is not None
    assert found.name == "Sleep Token"
    assert await async_artist_repository.count() == 7


@pytest.mark.asyncio
async def test_save_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="entity must not be None"):
        await async_artist_repository.save(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_save_all(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    new_artists = [
        Artist(name="Sleep Token", genre=Genre.ROCK, is_active=True),
        Artist(name="Spiritbox", genre=Genre.METAL, is_active=True),
    ]
    saved = await async_artist_repository.save_all(new_artists)
    await async_session.commit()

    assert len(saved) == 2
    assert all(a.id is not None for a in saved)
    assert await async_artist_repository.count() == 8


@pytest.mark.asyncio
async def test_save_all_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="entities must not contain None"):
        await async_artist_repository.save_all([Artist(name="Valid"), None])  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_delete(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    artist = await async_artist_repository.find_by_id(6)
    assert artist is not None
    await async_artist_repository.delete(artist)
    await async_session.commit()

    assert await async_artist_repository.find_by_id(6) is None
    assert await async_artist_repository.count() == 5


@pytest.mark.asyncio
async def test_delete_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="entity must not be None"):
        await async_artist_repository.delete(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_delete_by_id(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    await async_artist_repository.delete_by_id(6)
    await async_session.commit()

    assert await async_artist_repository.find_by_id(6) is None
    assert await async_artist_repository.count() == 5


@pytest.mark.asyncio
async def test_delete_by_id_not_found(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    await async_artist_repository.delete_by_id(9999)
    await async_session.commit()

    assert await async_artist_repository.count() == 6


@pytest.mark.asyncio
async def test_delete_by_id_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="_id must not be None"):
        await async_artist_repository.delete_by_id(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_delete_all_by_id(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    await async_artist_repository.delete_all_by_id([1, 2, 3])
    await async_session.commit()

    assert await async_artist_repository.count() == 3


@pytest.mark.asyncio
async def test_delete_all_by_id_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="ids must not contain None"):
        await async_artist_repository.delete_all_by_id([1, None])  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_delete_all(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    await async_artist_repository.delete_all()
    await async_session.commit()

    assert await async_artist_repository.count() == 0


@pytest.mark.asyncio
async def test_delete_all_with_entities(
    async_artist_repository: AsyncArtistRepository, async_session: AsyncSession
) -> None:
    artists = await async_artist_repository.find_all()
    await async_artist_repository.delete_all(artists)
    await async_session.commit()

    assert await async_artist_repository.count() == 0


@pytest.mark.asyncio
async def test_delete_all_entities_none_raises(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    with pytest.raises(ValueError, match="entities must not contain None"):
        await async_artist_repository.delete_all([None])  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_find_by_name(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    artists = await async_artist_repository.find_by_name("Amy Winehouse")
    assert len(artists) == 1
    assert artists[0].id == 3
