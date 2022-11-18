import typing as t
import datetime
import base64
import json

import pydantic
import requests


class MeteomaticsError(Exception):
    def __init__(self, status_code: int | None, detail: dict | str | None):
        self.status_code = status_code
        self.detail = detail


def get_access_token(
    username: str,
    password: str,
) -> str:
    auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
    response = requests.get(
        "https://login.meteomatics.com/api/v1/token",
        headers={"Authorization": f"Basic {auth_header}"},
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise MeteomaticsError(response.status_code, detail)
    return response.json()["access_token"]


class DateTimeForecast(pydantic.BaseModel):
    dt: datetime.datetime
    temperature_celsius: float
    wind_speed_meters_per_second: float
    precipitation_mm_per_hour: float
    symbol_index: int

    @property
    def symbol_description(self) -> str:
        mapping = {
            0: "Unknown",
            1: "Clear sky",
            2: "Light clouds",
            3: "Partly cloudy",
            4: "Cloudy",
            5: "Rain",
            6: "Rain and snow/sleet",
            7: "Snow",
            8: "Rain shower",
            9: "Snow shower",
            10: "Sleet shower",
            11: "Light Fog",
            12: "Dense fog",
            13: "Freezing rain",
            14: "Thunderstorms",
            15: "Drizzle",
            16: "Sandstorm",
        }
        if self.symbol_index >= 100:
            return f"{mapping[self.symbol_index - 100]} (night)"
        else:
            return mapping[self.symbol_index]

    @classmethod
    def parse_from_response(
        cls,
        meteomatics_response: t.Any,
        dt: datetime.datetime,
    ) -> "DateTimeForecast":
        temperature = cls._get_parameter(meteomatics_response, "t_2m:C", dt)
        windspeed = cls._get_parameter(meteomatics_response, "wind_speed_10m:ms", dt)
        precipitation = cls._get_parameter(meteomatics_response, "precip_1h:mm", dt)
        symbol_index = cls._get_parameter(
            meteomatics_response, "weather_symbol_1h:idx", dt
        )
        return DateTimeForecast(
            dt=dt,
            temperature_celsius=temperature,
            wind_speed_meters_per_second=windspeed,
            precipitation_mm_per_hour=precipitation,
            symbol_index=symbol_index,
        )

    @staticmethod
    def _get_parameter(
        meteomatics_response: t.Any, parameter: str, dt: datetime.datetime
    ) -> t.Any:
        data: t.Any = meteomatics_response.json()["data"]
        data = [d for d in data if d["parameter"] == parameter]
        assert len(data) == 1
        data = data[0]
        assert len(data["coordinates"]) == 1
        data = data["coordinates"][0]["dates"]
        dt_formatted = (
            dt.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        )
        data = [d for d in data if d["date"] == dt_formatted]
        assert len(data) == 1
        data = data[0]
        return data["value"]


class Forecast(pydantic.BaseModel):
    latitude: float
    longitude: float
    datetimes: dict[datetime.datetime, DateTimeForecast]


def get_forecast(
    access_token: str,
    latitude: float,
    longitude: float,
    datetimes: list[datetime.datetime],  # tz aware
) -> Forecast:
    datetimes_parameter = ",".join([dt.isoformat() for dt in sorted(datetimes)])
    parameters_parameter = "t_2m:C,wind_speed_10m:ms,precip_1h:mm,weather_symbol_1h:idx"
    location_parameter = f"{latitude},{longitude}"

    response = requests.post(
        f"https://api.meteomatics.com/{datetimes_parameter}",
        data=f"{parameters_parameter}/{location_parameter}/json",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "text/plain",
        },
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise MeteomaticsError(response.status_code, detail)

    return Forecast(
        latitude=latitude,
        longitude=longitude,
        datetimes={
            dt: DateTimeForecast.parse_from_response(response, dt) for dt in datetimes
        },
    )
