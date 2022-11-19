import json

import requests

import weatherforecastcli.errors as errors


def geocode(access_key: str, location_query: str) -> "GeocodedLocation":
    from weatherforecastcli.geocoding import GeocodedLocation

    response = requests.get(
        "http://api.positionstack.com/v1/forward?"
        f"access_key={access_key}&query={location_query}&timezone_module=1"
    )
    if not response.ok:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise errors.PositionstackError(
            f"status={response.status_code},detail={detail}"
        )

    geo_data = response.json()["data"][0]
    return GeocodedLocation(
        latitude=round(geo_data["latitude"], 4),
        longitude=round(geo_data["longitude"], 4),
        name=geo_data["name"],
        country_name=geo_data["country"],
        country_code=geo_data["country_code"],
        timezone_name=geo_data["timezone_module"]["name"],
    )
