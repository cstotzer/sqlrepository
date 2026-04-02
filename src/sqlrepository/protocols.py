"""Protocol definitions for the repository pattern.

This module provides ``@runtime_checkable`` :class:`typing.Protocol` classes
that describe the full public interface of the sync and async repositories.
Users should type-hint service dependencies against these protocols rather
than concrete repository classes, enabling structural subtyping and
dependency injection without importing SQLAlchemy or SQLModel.

Example::

    from sqlrepository.protocols import RepositoryProtocol

    class ArtistService:
        def __init__(self, repo: RepositoryProtocol[Artist, int]) -> None:
            self._repo = repo
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

_EntityT = TypeVar("_EntityT")
_IdT_contra = TypeVar("_IdT_contra", contravariant=True)


@runtime_checkable
class RepositoryProtocol(Protocol[_EntityT, _IdT_contra]):
    """Protocol describing the full public interface of a sync repository.

    Both :class:`sqlrepository.core.Repository` and
    :class:`sqlrepository.sqlmodel.Repository` satisfy this protocol.

    Type-hint service dependencies against this protocol to allow
    structural subtyping and easy mocking without importing ORM classes::

        from sqlrepository.protocols import RepositoryProtocol

        class ArtistService:
            def __init__(
                self, repo: RepositoryProtocol[Artist, int]
            ) -> None:
                self._repo = repo
    """

    def save(self, entity: _EntityT) -> _EntityT:
        """Saves a given entity to the database.

        Args:
            entity (EntityType): The entity to save. Must not be None.

        Returns:
            EntityType: The saved entity.

        Raises:
            ValueError: If the entity is None.
        """
        ...

    def save_all(self, entities: Iterable[_EntityT]) -> Sequence[_EntityT]:
        """Saves all given entities to the database.

        Args:
            entities (Iterable[EntityType]): The entities to save.

        Returns:
            Sequence[EntityType]: The saved entities.

        Raises:
            ValueError: If any entity is None.
        """
        ...

    def find_all(
        self,
        order_by: object | None = None,
        where: object | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[_EntityT]:
        """Returns all instances of the model type.

        Args:
            order_by: Optional column expression to order results by.
            where: Optional filter clause (v0.5, reserved for future use).
            limit: Optional maximum number of results to return
                (v0.5, reserved for future use).
            offset: Optional number of results to skip
                (v0.5, reserved for future use).

        Returns:
            Sequence[EntityType]: All (matching) entities.
        """
        ...

    def find_by_id(self, _id: _IdT_contra) -> _EntityT | None:
        """Retrieves an entity by its id.

        Args:
            _id (IdType): The identifier of the entity. Must not be None.

        Returns:
            EntityType | None: The entity, or None if not found.

        Raises:
            ValueError: If _id is None.
        """
        ...

    def find_all_by_id(self, ids: Iterable[_IdT_contra]) -> Sequence[_EntityT]:
        """Returns all entities matching the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers to look up.

        Returns:
            Sequence[EntityType]: The found entities.

        Raises:
            ValueError: If any id is None.
        """
        ...

    def exists_by_id(self, _id: _IdT_contra) -> bool:
        """Returns whether an entity with the given id exists.

        Args:
            _id (IdType): The identifier to check. Must not be None.

        Returns:
            bool: True if an entity exists, False otherwise.

        Raises:
            ValueError: If _id is None.
        """
        ...

    def count(
        self,
        where: object | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> int:
        """Returns the number of entities available.

        Args:
            where: Optional filter clause (v0.5, reserved for future use).
            limit: Optional maximum number of rows to consider
                (v0.5, reserved for future use).
            offset: Optional number of rows to skip
                (v0.5, reserved for future use).

        Returns:
            int: The count of (matching) entities.
        """
        ...

    def delete(self, entity: _EntityT) -> None:
        """Deletes a given entity from the database.

        Args:
            entity (EntityType): The entity to delete. Must not be None.

        Raises:
            ValueError: If the entity is None.
        """
        ...

    def delete_by_id(self, _id: _IdT_contra) -> None:
        """Deletes the entity with the given id.

        Args:
            _id (IdType): The identifier of the entity to delete.
                Must not be None.

        Raises:
            ValueError: If _id is None.
        """
        ...

    def delete_all(self, entities: Iterable[_EntityT] | None = None) -> None:
        """Deletes all entities, or all given entities if provided.

        Args:
            entities (Iterable[EntityType] | None): The entities to
                delete. If None, deletes all entities.

        Raises:
            ValueError: If any entity in the iterable is None.
        """
        ...

    def delete_all_by_id(self, ids: Iterable[_IdT_contra]) -> None:
        """Deletes all entities with the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities
                to delete.

        Raises:
            ValueError: If any id is None.
        """
        ...


@runtime_checkable
class AsyncRepositoryProtocol(Protocol[_EntityT, _IdT_contra]):
    """Protocol describing the full public interface of an async repository.

    Both :class:`sqlrepository.asyncio.AsyncRepository` and
    :class:`sqlrepository.sqlmodel.AsyncRepository` satisfy this protocol.

    Type-hint service dependencies against this protocol to allow
    structural subtyping and easy mocking without importing ORM classes::

        from sqlrepository.protocols import AsyncRepositoryProtocol

        class ArtistService:
            def __init__(
                self, repo: AsyncRepositoryProtocol[Artist, int]
            ) -> None:
                self._repo = repo
    """

    async def save(self, entity: _EntityT) -> _EntityT:
        """Saves a given entity to the database.

        Args:
            entity (EntityType): The entity to save. Must not be None.

        Returns:
            EntityType: The saved entity.

        Raises:
            ValueError: If the entity is None.
        """
        ...

    async def save_all(
        self, entities: Iterable[_EntityT]
    ) -> Sequence[_EntityT]:
        """Saves all given entities to the database.

        Args:
            entities (Iterable[EntityType]): The entities to save.

        Returns:
            Sequence[EntityType]: The saved entities.

        Raises:
            ValueError: If any entity is None.
        """
        ...

    async def find_all(
        self,
        order_by: object | None = None,
        where: object | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[_EntityT]:
        """Returns all instances of the model type.

        Args:
            order_by: Optional column expression to order results by.
            where: Optional filter clause (v0.5, reserved for future use).
            limit: Optional maximum number of results to return
                (v0.5, reserved for future use).
            offset: Optional number of results to skip
                (v0.5, reserved for future use).

        Returns:
            Sequence[EntityType]: All (matching) entities.
        """
        ...

    async def find_by_id(self, _id: _IdT_contra) -> _EntityT | None:
        """Retrieves an entity by its id.

        Args:
            _id (IdType): The identifier of the entity. Must not be None.

        Returns:
            EntityType | None: The entity, or None if not found.

        Raises:
            ValueError: If _id is None.
        """
        ...

    async def find_all_by_id(
        self, ids: Iterable[_IdT_contra]
    ) -> Sequence[_EntityT]:
        """Returns all entities matching the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers to look up.

        Returns:
            Sequence[EntityType]: The found entities.

        Raises:
            ValueError: If any id is None.
        """
        ...

    async def exists_by_id(self, _id: _IdT_contra) -> bool:
        """Returns whether an entity with the given id exists.

        Args:
            _id (IdType): The identifier to check. Must not be None.

        Returns:
            bool: True if an entity exists, False otherwise.

        Raises:
            ValueError: If _id is None.
        """
        ...

    async def count(
        self,
        where: object | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> int:
        """Returns the number of entities available.

        Args:
            where: Optional filter clause (v0.5, reserved for future use).
            limit: Optional maximum number of rows to consider
                (v0.5, reserved for future use).
            offset: Optional number of rows to skip
                (v0.5, reserved for future use).

        Returns:
            int: The count of (matching) entities.
        """
        ...

    async def delete(self, entity: _EntityT) -> None:
        """Deletes a given entity from the database.

        Args:
            entity (EntityType): The entity to delete. Must not be None.

        Raises:
            ValueError: If the entity is None.
        """
        ...

    async def delete_by_id(self, _id: _IdT_contra) -> None:
        """Deletes the entity with the given id.

        Args:
            _id (IdType): The identifier of the entity to delete.
                Must not be None.

        Raises:
            ValueError: If _id is None.
        """
        ...

    async def delete_all(
        self, entities: Iterable[_EntityT] | None = None
    ) -> None:
        """Deletes all entities, or all given entities if provided.

        Args:
            entities (Iterable[EntityType] | None): The entities to
                delete. If None, deletes all entities.

        Raises:
            ValueError: If any entity in the iterable is None.
        """
        ...

    async def delete_all_by_id(self, ids: Iterable[_IdT_contra]) -> None:
        """Deletes all entities with the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities
                to delete.

        Raises:
            ValueError: If any id is None.
        """
        ...


__all__ = ["AsyncRepositoryProtocol", "RepositoryProtocol"]
