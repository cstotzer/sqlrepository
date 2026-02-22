import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from sqlrepository import AsyncRepository, Repository
from tests.sqlalchemy.models import Artist
from tests.sqlalchemy.repositories import ArtistRepository


def test_init_subclass_skips_non_generic_base() -> None:
    """Test that __init_subclass__ skips non-generic bases via continue.

    Verifies that when a subclass mixes in a plain (non-generic) base
    alongside AsyncRepository[Model, Id], the loop continues past the
    plain base and correctly sets the model attribute.
    """

    class PlainBase:
        pass

    class MixedRepo(PlainBase, Repository[Artist, int]):
        pass

    assert MixedRepo.model is Artist


def test_init_fails_without_model(session: Session) -> None:
    """Test that initializing a Repository subclass without a model raises.

    Verifies that if a Repository subclass does not specify a model type
    via Repository[Model, IdType], then initializing it raises a TypeError.
    """

    class NoModelRepo(Repository[int, int]):  # type: ignore[type-var]
        pass

    with pytest.raises(
        TypeError,
        match="NoModelRepo must specify a model via Repository\\[Model, IdType\\]",  # noqa: E501
    ):
        NoModelRepo(session)


def test_init_fails_without_model_async(async_session: AsyncSession) -> None:
    """Test that initializing a Repository subclass without a model raises.

    Verifies that if a Repository subclass does not specify a model type
    via AsyncRepository[Model, IdType], then initializing it raises a
    TypeError.
    """

    class NoModelRepo(AsyncRepository[int, int]):  # type: ignore[type-var]
        pass

    with pytest.raises(
        TypeError,
        match="NoModelRepo must specify a model via AsyncRepository\\[Model, IdType\\]",  # noqa: E501
    ):
        NoModelRepo(async_session)


def test_init_subclass_skips_non_generic_base_async() -> None:
    """Test that __init_subclass__ skips non-generic bases via continue.

    Verifies that when a subclass mixes in a plain (non-generic) base
    alongside AsyncRepository[Model, Id], the loop continues past the
    plain base and correctly sets the model attribute.
    """

    class PlainBase:
        pass

    class MixedRepo(PlainBase, AsyncRepository[Artist, int]):
        pass

    assert MixedRepo.model is Artist


def test_session(session: Session) -> None:
    """Test that the session fixture is properly set up."""
    assert session is not None


def test_repositories(artist_repository: ArtistRepository) -> None:
    """Test that repositories are properly set up."""
    count = artist_repository.count()
    assert count == 6
