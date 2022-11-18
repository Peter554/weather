from __future__ import annotations

import datetime
import enum
import typing as t
import dataclasses
import json
import pathlib
import base64


import rich
import rich.console
import rich.table
import typer
import requests


app = typer.Typer()
console = rich.console.Console()


@dataclasses.dataclass(kw_only=True)
class Config:
    meteomatics_username: str
    meteomatics_password: str

    @classmethod
    def _path(cls) -> pathlib.Path:
        return pathlib.Path(pathlib.Path.home(), ".weather/config.json")

    def save(self) -> None:
        self._path().parent.mkdir(parents=True, exist_ok=True)
        with open(self._path(), "w") as f:
            json.dump(dataclasses.asdict(self), f)

    @classmethod
    def load(cls) -> t.Optional[Config]:
        if not cls._path().exists():
            return None
        with open(cls._path()) as f:
            return cls(**json.load(f))


@app.command()
def init(
    meteomatics_username: str = typer.Option(..., prompt=True),
    meteomatics_password: str = typer.Option(..., prompt=True),
) -> None:
    """
    Initializes the CLI, setting the user credentials.
    """
    config = Config(
        meteomatics_username=meteomatics_username,
        meteomatics_password=meteomatics_password,
    )
    config.save()


class ForcastResolution(str, enum.Enum):
    ONE_HOUR = "1H"
    TWO_HOUR = "2H"
    THREE_HOUR = "3H"
    FOUR_HOUR = "4H"
    SIX_HOUR = "6H"
    TWELVE_HOUR = "12H"


@app.command()
def forecast(
    skip_days: int = 0,
    take_days: int = 3,
    resolution: ForcastResolution = ForcastResolution.THREE_HOUR,
) -> None:
    """
    Fetch and display a weather forecast.
    """
    config = Config.load()
    if config is None:
        rich.print("[bold red]Missing config![/]")
        rich.print("Run `init` to initialize the CLI.")
        raise typer.Exit(code=1)

    meteomatics_auth_header = base64.b64encode(
        f"{config.meteomatics_username}:{config.meteomatics_password}".encode()
    ).decode()
    meteomatics_auth_response = requests.get(
        "https://login.meteomatics.com/api/v1/token",
        headers={"Authorization": f"Basic {meteomatics_auth_header}"},
    )
    if meteomatics_auth_response.status_code != 200:
        rich.print("[bold red]Failed to fetch meteomatics access token![/]")
        rich.print("status code:", meteomatics_auth_response.status_code)
        rich.print("detail:", meteomatics_auth_response.json())
        raise typer.Exit(code=1)

    location_coordinates = "52.39,13.06"  # TODO
    location_timezone_offset = "+01:00"

    meteomatics_access_token = meteomatics_auth_response.json()["access_token"]
    meteomatics_response = requests.post(
        f"https://api.meteomatics.com/"
        f"today+{skip_days}DT00:00:00{location_timezone_offset}"
        f"--today+{skip_days+take_days-1}DT24:00:00{location_timezone_offset}"
        f":PT{resolution}",
        data=f"t_2m:C,wind_speed_10m:ms,precip_1h:mm,weather_symbol_1h:idx/{location_coordinates}/json",
        headers={
            "Authorization": f"Bearer {meteomatics_access_token}",
            "Content-Type": "text/plain",
        },
    )
    if (
        meteomatics_response.status_code != 200
        or meteomatics_response.json()["status"] != "OK"
    ):
        rich.print("[bold red]Failed to fetch forecast from meteomatics![/]")
        rich.print("status code:", meteomatics_auth_response.status_code)
        rich.print("detail:", meteomatics_auth_response.json())
        raise typer.Exit(code=1)

    for delta_day in range(skip_days, skip_days + take_days):
        day = datetime.date.today() + datetime.timedelta(days=delta_day)

        table = rich.table.Table(title=str(day))
        table.add_column("Summary", justify="right")
        table.add_column("Time", justify="left")
        table.add_column("Temperature (°C)", justify="right")
        table.add_column("Wind speed (m/s)", justify="right")
        table.add_column("Precipitation (mm/h)", justify="right")


        resolution_timestep = {
            ForcastResolution.ONE_HOUR: datetime.timedelta(hours=1),
            ForcastResolution.TWO_HOUR: datetime.timedelta(hours=2),
            ForcastResolution.THREE_HOUR: datetime.timedelta(hours=3),
            ForcastResolution.FOUR_HOUR: datetime.timedelta(hours=4),
            ForcastResolution.SIX_HOUR: datetime.timedelta(hours=6),
            ForcastResolution.TWELVE_HOUR: datetime.timedelta(hours=12),
        }[resolution]
        timezone = _parse_timezone(location_timezone_offset)
        dt = datetime.datetime.combine(
            day, datetime.time(0, 0, 0), timezone
        )
        while True:
            if dt > datetime.datetime.now(timezone):
                temperature = _get_parameter(meteomatics_response, "t_2m:C", dt)
                windspeed = _get_parameter(meteomatics_response, "wind_speed_10m:ms", dt)
                precipitation = _get_parameter(meteomatics_response, "precip_1h:mm", dt)
                symbol_index = _get_parameter(
                    meteomatics_response, "weather_symbol_1h:idx", dt
                )
                summary = _get_summary(symbol_index)
                table.add_row(
                    str(dt.time()),
                    summary,
                    _colorize_temperature(temperature),
                    str(windspeed),
                    str(precipitation),
                )
            dt += resolution_timestep
            if dt.date() > day:
                break



        console.print(table)


def _parse_timezone(location_timezone_offset: str) -> datetime.timezone:
    return datetime.timezone(datetime.timedelta(hours=1))  # TODO


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


def _colorize_temperature(temperature: float) -> str:
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


def _get_summary(symbol_index: int) -> str:
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
    if symbol_index >= 100:
        return f"{mapping[symbol_index-100]} (night)"
    else:
        return mapping[symbol_index]


if __name__ == "__main__":
    app()
