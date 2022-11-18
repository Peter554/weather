import rich
import rich.console
import rich.table
import typer

import weatherforecastcli.meteomatics as meteomatics
import weatherforecastcli.positionstack as positionstack
import weatherforecastcli.utils as utils
from weatherforecastcli.config import Config

app = typer.Typer(help="Weather forecast CLI.")
console = rich.console.Console()


@app.command()
def init(
    meteomatics_username: str = typer.Option(..., prompt=True),
    meteomatics_password: str = typer.Option(..., prompt=True),
    positionstack_access_key: str = typer.Option(..., prompt=True),
) -> None:
    """
    Initializes the CLI, setting the user credentials.
    """
    config = Config(
        meteomatics_username=meteomatics_username,
        meteomatics_password=meteomatics_password,
        positionstack_access_key=positionstack_access_key,
    )
    config.save()


@app.command()
def forecast(
    location: str,
    skip_days: int = 0,
    take_days: int = 2,
    resolution: utils.ForcastResolution = utils.ForcastResolution.THREE_HOUR,
) -> None:
    """
    Fetch and display a weather forecast.
    """
    config = Config.load()
    if config is None:
        rich.print("[bold red]Missing config![/]")
        rich.print("Run `init` to initialize the CLI.")
        raise typer.Exit(code=1)

    try:
        geocoded_location = positionstack.geocode(
            config.positionstack_access_key, location
        )
    except positionstack.PositionstackError as e:
        rich.print("[bold red]Failed to geocode via positionstack![/]")
        rich.print("status code: ", e.status_code)
        rich.print("detail: ", e.detail)
        raise typer.Exit(code=1)

    datetimes = utils.build_forecast_datetimes(
        skip_days, take_days, resolution, geocoded_location.timezone_name
    )
    dates = set([dt.date() for dt in datetimes])

    try:
        access_token = meteomatics.get_access_token(
            username=config.meteomatics_username,
            password=config.meteomatics_password,
        )
        forecast = meteomatics.get_forecast(
            access_token=access_token,
            latitude=geocoded_location.latitude,
            longitude=geocoded_location.longitude,
            datetimes=datetimes,
        )
    except meteomatics.MeteomaticsError as e:
        rich.print("[bold red]Failed to call meteometrics![/]")
        rich.print("status code: ", e.status_code)
        rich.print("detail: ", e.detail)
        raise typer.Exit(code=1)

    rich.print(f"Forcast for [bold]{geocoded_location}[/]")
    for date in sorted(dates):
        table = rich.table.Table(title=str(date))
        table.add_column("Time", justify="left")
        table.add_column("Summary", justify="right")
        table.add_column("Temperature (°C)", justify="right")
        table.add_column("Wind speed (m/s)", justify="right")
        table.add_column("Precipitation (mm/h)", justify="right")

        for dt in sorted([dt for dt in datetimes if dt.date() == date]):
            dt_forecast = forecast.datetimes[dt]
            table.add_row(
                str(dt.time()),
                dt_forecast.symbol_description,
                utils.colorize_temperature(dt_forecast.temperature_celsius),
                str(dt_forecast.wind_speed_meters_per_second),
                str(dt_forecast.precipitation_mm_per_hour),
            )

        console.print(table)


def main():
    app()
