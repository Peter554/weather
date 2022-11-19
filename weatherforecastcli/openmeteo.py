import collections
import datetime
import json

import pydantic
import requests

import weatherforecastcli.utils as utils
import weatherforecastcli.errors as errors


class ForecastHour(pydantic.BaseModel):
    hour: datetime.datetime
    #
    temperature_celsius: float
    apparent_temperature_celsius: float
    #
    precipitation_mm: float
    snowfall_cm: float
    #
    windspeed_meters_per_second: float
    wind_direction_degrees: float
    #
    weathercode: int


class ForecastDay(pydantic.BaseModel):
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
    #
    hours: dict[datetime.datetime, ForecastHour]


class Forecast(pydantic.BaseModel):
    days: dict[datetime.date, ForecastDay]


def get_forecast(
    *,
    latitude: float,
    longitude: float,
    start_date: datetime.date,
    end_date: datetime.date,
) -> Forecast:
    qs = (
        f"latitude={latitude}&longitude={longitude}&timezone=auto"
        "&temperature_unit=celsius&windspeed_unit=ms&precipitation_unit=mm&timeformat=iso8601"
        f"&start_date={start_date}&end_date={end_date}"
        # daily parameters
        "&daily=temperature_2m_min,temperature_2m_max,apparent_temperature_min,apparent_temperature_max,"
        "precipitation_sum,precipitation_hours,snowfall_sum,"
        "windspeed_10m_max,winddirection_10m_dominant,weathercode,sunrise,sunset"
        # hourly parameters
        "&hourly=temperature_2m,apparent_temperature,windspeed_10m,winddirection_10m,precipitation,snowfall,weathercode"
    )

    response = requests.get(f"https://api.open-meteo.com/v1/forecast?{qs}")
    if not response.ok:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        raise errors.OpenmeteoError(f"status={response.status_code},detail={detail}")

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
    assert data["hourly_units"] == {  # sanity check
        "time": "iso8601",
        "temperature_2m": "°C",
        "apparent_temperature": "°C",
        "windspeed_10m": "m/s",
        "winddirection_10m": "°",
        "precipitation": "mm",
        "snowfall": "cm",
        "weathercode": "wmo code",
    }

    daily_dates = [utils.parse_date(d) for d in data["daily"]["time"]]

    hours = [
        datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in data["hourly"]["time"]
    ]
    forecast_hours_by_date: dict[
        datetime.date, dict[datetime.datetime, ForecastHour]
    ] = collections.defaultdict(dict)
    for idx, hour in enumerate(hours):
        forecast_hours_by_date[hour.date()][hour] = ForecastHour(
            hour=hour,
            temperature_celsius=data["hourly"]["temperature_2m"][idx],
            apparent_temperature_celsius=data["hourly"]["apparent_temperature"][idx],
            precipitation_mm=data["hourly"]["precipitation"][idx],
            snowfall_cm=data["hourly"]["snowfall"][idx],
            windspeed_meters_per_second=data["hourly"]["windspeed_10m"][idx],
            wind_direction_degrees=data["hourly"]["winddirection_10m"][idx],
            weathercode=data["hourly"]["weathercode"][idx],
        )

    return Forecast(
        days={
            d: ForecastDay(
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
                hours=forecast_hours_by_date[d],
            )
            for idx, d in enumerate(daily_dates)
        }
    )
