import zoneinfo
import datetime
import enum


class ForcastResolution(str, enum.Enum):
    ONE_HOUR = "1H"
    TWO_HOUR = "2H"
    THREE_HOUR = "3H"
    FOUR_HOUR = "4H"
    SIX_HOUR = "6H"
    TWELVE_HOUR = "12H"


resolution_timedelta_mapping = {
    ForcastResolution.ONE_HOUR: datetime.timedelta(hours=1),
    ForcastResolution.TWO_HOUR: datetime.timedelta(hours=2),
    ForcastResolution.THREE_HOUR: datetime.timedelta(hours=3),
    ForcastResolution.FOUR_HOUR: datetime.timedelta(hours=4),
    ForcastResolution.SIX_HOUR: datetime.timedelta(hours=6),
    ForcastResolution.TWELVE_HOUR: datetime.timedelta(hours=12),
}


def build_forecast_datetimes(
    skip_days: int, take_days: int, resolution: ForcastResolution, timezone_name: str
) -> list[datetime.datetime]:
    location_timezone = zoneinfo.ZoneInfo(timezone_name)
    today_in_timezone = datetime.datetime.now(location_timezone).date()
    start_dt = datetime.datetime.combine(
        today_in_timezone + datetime.timedelta(days=skip_days),
        datetime.time(0, 0, 0),
        location_timezone,
    )
    end_date = datetime.datetime.combine(
        start_dt + datetime.timedelta(days=take_days - 1),
        datetime.time(0, 0, 0),
        location_timezone,
    ).date()

    datetimes = [start_dt]
    while True:
        next_dt = datetimes[-1] + resolution_timedelta_mapping[resolution]
        if next_dt.date() > end_date:
            break
        datetimes.append(next_dt)
    return sorted(
        [dt for dt in datetimes if dt >= datetime.datetime.now(location_timezone)]
    )


def colorize_temperature(temperature: float) -> str:
    if temperature >= 30:
        color = "red"
    elif temperature >= 20:
        color = "orange"
    elif temperature >= 10:
        color = "yellow"
    elif temperature >= 0:
        color = "white"
    else:
        color = "blue"
    return f"[{color}]{temperature}[/]"
