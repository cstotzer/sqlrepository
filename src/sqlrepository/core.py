from __future__ import annotations

from collections.abc import Iterable, Sequence
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

from sqlalchemy import ColumnExpressionArgument, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Session

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from sqlmodel import SQLModel

    EntityType = TypeVar("EntityType", bound=DeclarativeBase | SQLModel)
else:
    EntityType = TypeVar("EntityType", bound=DeclarativeBase)


IdType = TypeVar("IdType")


logger = getLogger(__name__)


class BaseRepository(Generic[EntityType, IdType]):
    """Base repository providing all CRUD operations.

    This class defines the complete repository interface and implementation
    shared across all concrete repository types (SQLAlchemy, SQLModel, etc.).
    Subclasses are responsible for session management and model type
    resolution via ``__init_subclass__``.
    """

    model: type[Any]
    session: Session

    def _model_type(self) -> type[EntityType]:
        """Returns the model type associated with this repository.

        Returns:
            type[EntityType]: The model class.
        """
        return cast("type[EntityType]", self.__class__.model)

    def save(self, entity: EntityType) -> EntityType:
        """Saves a given entity to the database.

        Args:
            entity (EntityType): The entity to save. Must not be None.

        Returns:
            EntityType: The saved entity.

        Raises:
            ValueError: If the entity is None.
        """
        if entity is None:
            raise ValueError("entity must not be None")
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def save_all(self, entities: Iterable[EntityType]) -> Sequence[EntityType]:
        """Saves all given entities to the database.

        Args:
            entities (Iterable[EntityType]): The entities to save. Must not
                contain None.

        Returns:
            Sequence[EntityType]: The saved entities.

        Raises:
            ValueError: If any entity is None.
        """
        items = list(entities)
        if any(entity is None for entity in items):
            raise ValueError("entities must not contain None")
        self.session.add_all(items)
        self.session.flush()
        for entity in items:
            self.session.refresh(entity)
        return items

    def find_all(
        self,
        order_by: ColumnExpressionArgument[Any] | None = None,
    ) -> Sequence[EntityType]:
        """Returns all instances of the model type.

        Args:
            order_by: Optional column expression to order results by.

        Returns:
            Sequence[EntityType]: All entities in the database.
        """
        statement = select(self._model_type())

        if order_by is not None:
            statement = statement.order_by(order_by)

        return self.session.scalars(statement).all()

    def find_by_id(self, _id: IdType) -> EntityType | None:
        """Retrieves an entity by its id.

        Args:
            _id (IdType): The identifier of the entity. Must not be None.

        Returns:
            EntityType | None: The entity with the given id, or None if not
                found.

        Raises:
            ValueError: If _id is None.
        """
        if _id is None:
            raise ValueError("_id must not be None")
        return self.session.get(self._model_type(), _id)

    def exists_by_id(self, _id: IdType) -> bool:
        """Returns whether an entity with the given id exists.

        Args:
            _id (IdType): The identifier to check. Must not be None.

        Returns:
            bool: True if an entity with the given id exists, False otherwise.

        Raises:
            ValueError: If _id is None.
        """
        if _id is None:
            raise ValueError("_id must not be None")
        return self.find_by_id(_id) is not None

    def find_all_by_id(self, ids: Iterable[IdType]) -> Sequence[EntityType]:
        """Returns all entities matching the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities. Must not
                contain None.

        Returns:
            Sequence[EntityType]: The found entities. Entities not found are
                omitted.

        Raises:
            ValueError: If any id is None.
        """
        id_values = list(ids)
        if any(id_value is None for id_value in id_values):
            raise ValueError("ids must not contain None")

        entities: list[EntityType] = []
        for id_value in id_values:
            entity = self.find_by_id(id_value)
            if entity is not None:
                entities.append(entity)
        return entities

    def count(self) -> int:
        """Returns the number of entities available.

        Returns:
            int: The count of entities in the database.
        """
        statement = select(func.count()).select_from(self._model_type())
        return int(self.session.scalar(statement) or 0)

    def delete_by_id(self, _id: IdType) -> None:
        """Deletes the entity with the given id.

        Args:
            _id (IdType): The identifier of the entity to delete. Must not be
                None.

        Raises:
            ValueError: If _id is None.
        """
        if _id is None:
            raise ValueError("_id must not be None")
        entity = self.find_by_id(_id)
        if entity is not None:
            self.session.delete(entity)

    def delete(self, entity: EntityType) -> None:
        """Deletes a given entity from the database.

        Args:
            entity (EntityType): The entity to delete. Must not be None.

        Raises:
            ValueError: If the entity is None.
        """
        if entity is None:
            raise ValueError("entity must not be None")
        self.session.delete(entity)

    def delete_all_by_id(self, ids: Iterable[IdType]) -> None:
        """Deletes all entities with the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities to delete.
                Must not contain None.

        Raises:
            ValueError: If any id is None.
        """
        id_values = list(ids)
        if any(id_value is None for id_value in id_values):
            raise ValueError("ids must not contain None")
        for id_value in id_values:
            self.delete_by_id(id_value)

    def delete_all(self, entities: Iterable[EntityType] | None = None) -> None:
        """Deletes all entities or all given entities if provided.

        Args:
            entities (Iterable[EntityType] | None): The entities to delete. If
                None, deletes all entities of the model type.

        Raises:
            ValueError: If any entity in the provided iterable is None.
        """
        if entities is None:
            statement = delete(self._model_type())
            self.session.execute(statement)
            return

        items = list(entities)
        if any(entity is None for entity in items):
            raise ValueError("entities must not contain None")
        for entity in items:
            self.session.delete(entity)


class Repository(BaseRepository[EntityType, IdType]):
    """Generic repository for SQLAlchemy DeclarativeBase models.

    This class is inspired by Spring Data's CrudRepository interface.
    Subclasses must specify the model type via Repository[Model, IdType].

    Example:
        ```python
        from sqlalchemy.orm import Mapped, Session, mapped_column
        from sqlrepository import Repository
        from sqlrepository.core import Base

        class Artist(Base):
            __tablename__ = "artists"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None]

        class ArtistRepository(Repository[Artist, int]):
            pass

        # Usage
        with Session(engine) as session:
            repo = ArtistRepository(session)
            artist = repo.find_by_id(1)
        ```
    """

    model: type[DeclarativeBase]

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
                and issubclass(args[0], DeclarativeBase)
            ):
                cls.model = args[0]
                return

    def __init__(self, session: Session) -> None:
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
                "via Repository[Model, IdType]"
            )
            raise TypeError(msg)
