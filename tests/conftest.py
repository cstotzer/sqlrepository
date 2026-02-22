import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

RESOURCES = Path(__file__).parent / "resources"

_DATE_FIELDS = {"birth_date", "release_date"}


class _DateTimeDecoder(json.JSONDecoder):
    """JSON decoder that converts known date fields to datetime objects."""

    def __init__(self, *args: tuple[Any], **kwargs) -> None:  # noqa: ANN003
        super().__init__(object_hook=self._object_hook, **kwargs)

    @staticmethod
    def _object_hook(obj: dict[str, Any]) -> dict[str, Any]:
        for field in _DATE_FIELDS:
            if field in obj and obj[field] is not None:
                obj[field] = datetime.fromisoformat(obj[field])
        return obj


@pytest.fixture(scope="session", autouse=True)
def test_data() -> tuple[list[dict], list[dict]]:
    """Load and deserialize artist and album test data from JSON files."""
    with Path(RESOURCES / "artists.json").open(encoding="utf-8") as f:
        artists = json.load(f, cls=_DateTimeDecoder)

    with Path(RESOURCES / "albums.json").open(encoding="utf-8") as f:
        albums = json.load(f, cls=_DateTimeDecoder)

    return artists, albums
