"""SQLModel test models.

This module defines SQLModel models for testing the SQLModel repository
    implementation.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlmodel import Field, Relationship, SQLModel


class Genre(StrEnum):
    POP = "pop"
    ROCK = "rock"
    METAL = "metal"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    OTHER = "other"


class Artist(SQLModel, table=True):
    """SQLModel artist model."""

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, max_length=120)
    genre: Genre | None = Field(default=Genre.OTHER)
    birth_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    is_active: bool = Field(
        default=True, sa_column=Column(Boolean, default=True)
    )

    albums: list["Album"] = Relationship(
        back_populates="artist", cascade_delete=True
    )


class Album(SQLModel, table=True):
    """SQLModel album model."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=160)
    release_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    rating: int | None = Field(
        default=3, sa_column=Column(Integer, nullable=True)
    )
    artist_id: int | None = Field(
        default=None, foreign_key="artist.id", ondelete="CASCADE"
    )
    artist: Artist | None = Relationship(back_populates="albums")
