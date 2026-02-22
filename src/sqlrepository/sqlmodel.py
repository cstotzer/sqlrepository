from typing import Any, get_args, get_origin

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, SQLModel

from sqlrepository.asyncio import BaseAsyncRepository
from sqlrepository.core import BaseRepository, EntityType, IdType


class Repository(BaseRepository[EntityType, IdType]):  # type: ignore[type-var]
    """Generic repository for SQLModel models.

    This class provides the same repository pattern as
    :class:`sqlrepository.core.Repository` but for SQLModel models with
    built-in Pydantic validation. Subclasses must specify the model type
    via Repository[Model, IdType].

    Example:
        ```python
        from sqlmodel import Field, Session, SQLModel
        from sqlrepository.sqlmodel import Repository

        class Artist(SQLModel, table=True):
            id: int | None = Field(default=None, primary_key=True)
            name: str | None = Field(default=None)

        class ArtistRepository(Repository[Artist, int]):
            pass

        # Usage
        with Session(engine) as session:
            repo = ArtistRepository(session)
            artist = repo.find_by_id(1)
        ```
    """

    model: type[SQLModel]  # type: ignore[assignment]

    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        """Initializes the subclass and sets the model type."""
        super().__init_subclass__(**kwargs)
        for base in getattr(cls, "__orig_bases__", ()):
            origin = get_origin(base)
            if origin is None or not (
                isinstance(origin, type) and issubclass(origin, Repository)
            ):
                continue
            args = get_args(base)
            if (
                args
                and isinstance(args[0], type)
                and issubclass(
                    args[0],
                    SQLModel,  # type: ignore[type-arg]
                )
            ):
                cls.model = args[0]
                return

    def __init__(self, session: Session) -> None:
        """Initializes the repository with a SQLModel session.

        Args:
            session (Session): The SQLModel session to use for database
                operations.

        Raises:
            TypeError: If the model type is not specified in the subclass.
        """
        self.session = session
        if not hasattr(self.__class__, "model"):
            msg = (
                f"{self.__class__.__name__} must specify a model "
                "via Repository[Model, IdType]"
            )
            raise TypeError(msg)


class AsyncRepository(
    BaseAsyncRepository[EntityType, IdType]  # type: ignore[type-var]
):
    """Generic async repository for SQLModel models.

    This class provides the same repository pattern as
    :class:`sqlrepository.asyncio.AsyncRepository` but for SQLModel models
    with built-in Pydantic validation. Subclasses must specify the model
    type via AsyncRepository[Model, IdType].

    Example:
        ```python
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import Field, SQLModel
        from sqlrepository.sqlmodel import AsyncRepository

        class Artist(SQLModel, table=True):
            id: int | None = Field(default=None, primary_key=True)
            name: str | None = Field(default=None)

        class ArtistRepository(AsyncRepository[Artist, int]):
            pass

        # Usage
        async with AsyncSession(engine) as session:
            repo = ArtistRepository(session)
            artist = await repo.find_by_id(1)
        ```
    """

    model: type[SQLModel]  # type: ignore[valid-type]

    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        """Initializes the subclass and sets the model type."""
        super().__init_subclass__(**kwargs)
        for base in getattr(cls, "__orig_bases__", ()):
            origin = get_origin(base)
            if origin is None or not (
                isinstance(origin, type)
                and issubclass(origin, AsyncRepository)
            ):
                continue
            args = get_args(base)
            if (
                args
                and isinstance(args[0], type)
                and issubclass(
                    args[0],
                    SQLModel,  # type: ignore[type-arg]
                )
            ):
                cls.model = args[0]
                return

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the repository with a SQLModel session.

        Args:
            session (AsyncSession): The async SQLAlchemy session to use for
                database operations.

        Raises:
            TypeError: If the model type is not specified in the subclass.
        """
        self.session = session
        if not hasattr(self.__class__, "model"):
            msg = (
                f"{self.__class__.__name__} must specify a model "
                "via AsyncRepository[Model, IdType]"
            )
            raise TypeError(msg)


__all__ = ["AsyncRepository", "Repository"]
