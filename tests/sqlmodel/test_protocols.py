"""Tests for RepositoryProtocol and AsyncRepositoryProtocol with SQLModel."""

from sqlrepository.protocols import AsyncRepositoryProtocol, RepositoryProtocol
from tests.sqlmodel.repositories import (
    ArtistRepository,
    AsyncArtistRepository,
)


def test_repository_satisfies_protocol(
    artist_repository: ArtistRepository,
) -> None:
    assert isinstance(artist_repository, RepositoryProtocol)


def test_async_repository_satisfies_protocol(
    async_artist_repository: AsyncArtistRepository,
) -> None:
    assert isinstance(async_artist_repository, AsyncRepositoryProtocol)


def test_plain_object_does_not_satisfy_protocol() -> None:
    assert not isinstance(object(), RepositoryProtocol)


def test_plain_object_does_not_satisfy_async_protocol() -> None:
    assert not isinstance(object(), AsyncRepositoryProtocol)
