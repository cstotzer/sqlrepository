from collections.abc import Sequence

from sqlalchemy import select

from sqlrepository import AsyncRepository, Repository
from tests.sqlalchemy.models import Artist


class ArtistRepository(Repository[Artist, int]):
    def find_by_name(self, name: str) -> Sequence[Artist]:
        """
        Finds artists by their name.

        Args:
            name (str): The name of the artist to search for.

        Returns:
            Sequence[Artist]: A sequence of artists matching the given name.
        """
        return self.session.query(Artist).filter_by(name=name).all()


class AsyncArtistRepository(AsyncRepository[Artist, int]):
    async def find_by_name(self, name: str) -> Sequence[Artist]:
        """
        Asynchronously finds artists by their name.

        Args:
            name (str): The name of the artist to search for.

        Returns:
            Sequence[Artist]: A sequence of artists matching the given name.
        """
        statement = select(Artist).filter_by(name=name)

        result = await self.session.scalars(statement)
        return result.all()
