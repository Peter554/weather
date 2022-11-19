import json

import pydantic
import requests


class PositionstackError(Exception):
    def __init__(self, status_code: int | None, detail: dict | str | None):
        self.status_code = status_code
        self.detail = detail


class GeocodedLocation(pydantic.BaseModel):
    latitude: float
    longitude: float
    name: str
    country_name: str
    country_code: str
    timezone_name: str
    timezone_offset_string: str


def geocode(access_key: str, location_query: str) -> GeocodedLocation:
    response = requests.get(
        "http://api.positionstack.com/v1/forward?"
        f"access_key={access_key}&query={location_query}&timezone_module=1"
    )
    if not response.ok:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise PositionstackError(response.status_code, detail)

    geo_data = response.json()["data"][0]
    return GeocodedLocation(
        latitude=round(geo_data["latitude"], 4),
        longitude=round(geo_data["longitude"], 4),
        name=geo_data["name"],
        country_name=geo_data["country"],
        country_code=geo_data["country_code"],
        timezone_name=geo_data["timezone_module"]["name"],
        timezone_offset_string=geo_data["timezone_module"]["offset_string"],
    )
