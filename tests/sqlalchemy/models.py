from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    NVARCHAR,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase): ...


class Genre(StrEnum):
    POP = "pop"
    ROCK = "rock"
    METAL = "metal"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    OTHER = "other"


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(NVARCHAR(120))
    genre: Mapped[Genre] = mapped_column(default=Genre.OTHER)
    birth_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    albums: Mapped[list["Album"]] = relationship(
        "Album", back_populates="artist", cascade="all, delete-orphan"
    )


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(NVARCHAR(160), nullable=False)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id"), nullable=False
    )

    artist: Mapped["Artist"] = relationship("Artist", back_populates="albums")
    # New fields
    release_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    rating: Mapped[int | None] = mapped_column(
        Integer, default=3, nullable=True
    )
