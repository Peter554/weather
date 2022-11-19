import json
import pathlib

import pydantic

import weatherforecastcli.positionstack as positionstack
from weatherforecastcli.config import APP_DIR


class GeocodedLocation(pydantic.BaseModel):
    latitude: float
    longitude: float
    name: str
    country_name: str
    country_code: str
    timezone_name: str


class GeocodingDB:
    def __init__(self):
        self._db: dict[str, GeocodedLocation] = {}

    def get(self, location_query: str) -> GeocodedLocation | None:
        return self._db.get(location_query)

    def set(self, location_query: str, geocoded_location: GeocodedLocation) -> None:
        self._db[location_query] = geocoded_location

    @classmethod
    def _path(cls) -> pathlib.Path:
        return pathlib.Path(APP_DIR, "geocodingdb.json")

    def save(self) -> None:
        self._path().parent.mkdir(parents=True, exist_ok=True)
        with open(self._path(), "w") as f:
            json.dump({k: v.dict() for k, v in self._db.items()}, f, indent=2)

    @classmethod
    def load(cls) -> "GeocodingDB":
        if cls._path().exists():
            with open(cls._path()) as f:
                db_data = json.load(f)
                o = cls()
                o._db = {k: GeocodedLocation.parse_obj(v) for k, v in db_data.items()}
                return o
        else:
            return cls()


def geocode(
    *,
    positionstack_access_key: str,
    location_query: str,
) -> GeocodedLocation:
    db = GeocodingDB.load()
    if cached_location := db.get(location_query):
        return cached_location
    positionstack_location = positionstack.geocode(
        positionstack_access_key, location_query
    )
    db.set(location_query, positionstack_location)
    db.save()
    return positionstack_location
