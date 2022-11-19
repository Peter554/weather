import datetime
import json

import pydantic
import requests

import weatherforecastcli.utils as utils


class OpenmeteoError(Exception):
    def __init__(self, status_code: int | None, detail: dict | str | None):
        self.status_code = status_code
        self.detail = detail


class DayForecast(pydantic.BaseModel):
    date: datetime.date
    #
    temperature_min_celsius: float
    temperature_max_celsius: float
    apparent_temperature_min_celsius: float
    apparent_temperature_max_celsius: float
    #
    total_precipitation_mm: float
    total_precipitation_hours: float
    total_snowfall_cm: float
    #
    max_windspeed_meters_per_second: float
    dominant_wind_direction_degrees: float
    #
    weathercode: int
    sunrise: datetime.datetime
    sunset: datetime.datetime


class DailyForecast(pydantic.BaseModel):
    days: dict[datetime.date, DayForecast]


def get_daily_forecast(
    *,
    latitude: float,
    longitude: float,
    start_date: datetime.date,
    end_date: datetime.date,
) -> DailyForecast:
    qs = (
        f"latitude={latitude}&longitude={longitude}&timezone=auto"
        "&temperature_unit=celsius&windspeed_unit=ms&precipitation_unit=mm&timeformat=iso8601"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_min,temperature_2m_max,apparent_temperature_min,apparent_temperature_max,"
        "precipitation_sum,precipitation_hours,snowfall_sum,"
        "windspeed_10m_max,winddirection_10m_dominant,weathercode,sunrise,sunset"
    )

    response = requests.get(f"https://api.open-meteo.com/v1/forecast?{qs}")
    if not response.ok:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise OpenmeteoError(response.status_code, detail)

    data = response.json()
    assert data["daily_units"] == {  # sanity check
        "time": "iso8601",
        "temperature_2m_min": "°C",
        "temperature_2m_max": "°C",
        "apparent_temperature_min": "°C",
        "apparent_temperature_max": "°C",
        "precipitation_sum": "mm",
        "precipitation_hours": "h",
        "snowfall_sum": "cm",
        "windspeed_10m_max": "m/s",
        "winddirection_10m_dominant": "°",
        "weathercode": "wmo code",
        "sunrise": "iso8601",
        "sunset": "iso8601",
    }

    dates = [utils.parse_date(d) for d in data["daily"]["time"]]
    return DailyForecast(
        days={
            d: DayForecast(
                date=d,
                temperature_min_celsius=data["daily"]["temperature_2m_min"][idx],
                temperature_max_celsius=data["daily"]["temperature_2m_max"][idx],
                apparent_temperature_min_celsius=data["daily"][
                    "apparent_temperature_min"
                ][idx],
                apparent_temperature_max_celsius=data["daily"][
                    "apparent_temperature_max"
                ][idx],
                total_precipitation_mm=data["daily"]["precipitation_sum"][idx],
                total_precipitation_hours=data["daily"]["precipitation_hours"][idx],
                total_snowfall_cm=data["daily"]["snowfall_sum"][idx],
                max_windspeed_meters_per_second=data["daily"]["windspeed_10m_max"][idx],
                dominant_wind_direction_degrees=data["daily"][
                    "winddirection_10m_dominant"
                ][idx],
                weathercode=data["daily"]["weathercode"][idx],
                sunrise=data["daily"]["sunrise"][idx],
                sunset=data["daily"]["sunset"][idx],
            )
            for idx, d in enumerate(dates)
        }
    )
