import datetime
import zoneinfo

import typer
from rich.console import Console


import weatherforecastcli.geocoding as geocoding
import weatherforecastcli.openmeteo as openmeteo
import weatherforecastcli.render as render
import weatherforecastcli.utils as utils
import weatherforecastcli.config as config
import weatherforecastcli.errors as errors

app = typer.Typer(name="weather", help="Weather forecast CLI.")
console = Console(style="white on grey15", record=True)


@app.command()
def init(
    positionstack_access_key: str = typer.Option(
        ..., prompt=True, help="Positionstack access key, used for geocoding."
    ),
) -> None:
    """
    Initializes the CLI.
    """
    config_ = config.Config(
        positionstack_access_key=positionstack_access_key,
    )
    config_.save()


@app.command()
def forecast(
    location: str,
    start_date: str | None = None,
    days: int = 4,
    export_svg: str | None = None,
) -> None:
    """
    Fetch and display a weather forecast.
    """
    try:
        config_ = config.Config.load()
    except errors.MissingConfigError:
        console.print("[bold red]Missing config.[/]")
        console.print("Run `init` to initialize the CLI.")
        raise typer.Exit(code=1)
    except errors.CorruptedConfigError:
        console.print("[bold red]Corrupted config.[/]")
        console.print("Run `init` to re-initialize the CLI.")
        raise typer.Exit(code=1)

    try:
        geocoded_location = geocoding.geocode(
            positionstack_access_key=config_.positionstack_access_key,
            location_query=location,
        )
    except errors.GeocodingError as e:
        console.print("[bold red]Failed to geocode.[/]")
        console.print("error: ", str(e))
        raise typer.Exit(code=1)

    location_timezone = zoneinfo.ZoneInfo(geocoded_location.timezone_name)
    today_at_location = datetime.datetime.now(location_timezone).date()
    start_date_date = (
        today_at_location if start_date is None else utils.parse_date(start_date)
    )
    end_date_date = start_date_date + datetime.timedelta(days=days - 1)

    try:
        daily_forecast = openmeteo.get_daily_forecast(
            latitude=geocoded_location.latitude,
            longitude=geocoded_location.longitude,
            start_date=start_date_date,
            end_date=end_date_date,
        )
    except errors.OpenmeteoError as e:
        console.print("[bold red]Failed to get forecast from Open-Meteo.[/]")
        console.print("error: ", str(e))
        raise typer.Exit(code=1)

    render.DailyForecastRenderer().render(console, geocoded_location, daily_forecast)

    if export_svg:
        with open(export_svg, "w") as f:
            f.write(console.export_svg())


def main():
    app()
