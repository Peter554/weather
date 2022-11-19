from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich.padding import Padding


from weatherforecastcli.geocoding import GeocodedLocation
from weatherforecastcli.openmeteo import Forecast, ForecastDay, ForecastHour


class SummaryForecastRenderer:
    def render(self, console, location: GeocodedLocation, forecast: Forecast):
        dates = sorted(forecast.days.keys())
        console.print(
            Panel(
                Group(
                    f"[bold]Weather forecast for\n[green]{location.name}, {location.country_name} ({location.latitude}, {location.longitude})[/][/]",
                    Padding(
                        Columns(
                            [self._render_day(forecast.days[d]) for d in dates],
                            equal=True,
                        ),
                        (1, 0, 0, 0),
                    ),
                )
            )
        )

    def _render_day(self, forecast: ForecastDay):
        table = Table(show_header=False, show_lines=True, expand=True)
        table.add_column("", justify="left")
        table.add_column("", justify="right")
        table.add_row("", f"[bold green]{forecast.date.strftime('%A %d %B')}[/]")
        table.add_row(
            "", WEATHERCODE_DESCRIPTION_MAPPING.get(forecast.weathercode, "-")
        )
        table.add_row(
            ":thermometer:",
            f"{colorize_temperature(forecast.temperature_min_celsius)}/{colorize_temperature(forecast.temperature_max_celsius)}°C "
            f"({colorize_temperature(forecast.apparent_temperature_min_celsius)}/{colorize_temperature(forecast.apparent_temperature_max_celsius)}°C)",
        )
        table.add_row(
            ":cloud_with_rain:",
            f"{forecast.total_precipitation_mm}mm, {round(forecast.total_precipitation_hours)}hr",
        )
        table.add_row(
            ":wind_face:",
            f"{forecast.max_windspeed_meters_per_second}m/s, {get_wind_direction(forecast.dominant_wind_direction_degrees)}",
        )
        table.add_row(
            ":sunrise:",
            f"{forecast.sunrise.strftime('%H:%M')}, {forecast.sunset.strftime('%H:%M')}",
        )
        return table


class DetailedForecastRenderer:
    def render(
        self,
        console,
        location: GeocodedLocation,
        forecast: Forecast,
        resolution_hours: int,
    ):
        dates = sorted(forecast.days.keys())
        console.print(
            Panel(
                Group(
                    f"[bold]Weather forecast for\n[green]{location.name}, {location.country_name} ({location.latitude}, {location.longitude})[/][/]",
                    Padding(
                        Group(
                            *[
                                self._render_day(forecast.days[d], resolution_hours)
                                for d in dates
                            ]
                        ),
                        (1, 0, 0, 0),
                    ),
                )
            )
        )

    def _render_day(self, forecast: ForecastDay, resolution_hours: int):
        hours = sorted(forecast.hours.keys())
        hours = [h for h in hours if h.hour % resolution_hours == 0]
        return Panel(
            Group(
                f"[bold green underline]{forecast.date.strftime('%A %d %B')}[/]",
                Padding(
                    Group(
                        f"[bold green]Summary:\t\t{WEATHERCODE_DESCRIPTION_MAPPING.get(forecast.weathercode, '-')}[/]",
                        f"[bold]Temperature:[/]\t\t{colorize_temperature(forecast.temperature_min_celsius)}/{colorize_temperature(forecast.temperature_max_celsius)}°C "
                        f"({colorize_temperature(forecast.apparent_temperature_min_celsius)}/{colorize_temperature(forecast.apparent_temperature_max_celsius)}°C)",
                        f"[bold]Precipitation:[/]\t\t{forecast.total_precipitation_mm}mm, {round(forecast.total_precipitation_hours)}hr",
                        f"[bold]Wind speed:[/]\t\t{forecast.max_windspeed_meters_per_second}m/s, {get_wind_direction(forecast.dominant_wind_direction_degrees)}",
                        f"[bold]Sunrise/Sunset:[/]\t\t{forecast.sunrise.strftime('%H:%M')}, {forecast.sunset.strftime('%H:%M')}",
                    ),
                    (1, 0, 0, 0),
                ),
                Padding(
                    self._render_hours([forecast.hours[h] for h in hours]), (1, 0, 0, 0)
                ),
            )
        )

    def _render_hours(self, forecasts: list[ForecastHour]):
        table = Table(show_lines=True, expand=True)
        table.add_column("Time", justify="left")
        table.add_column("Summary", justify="right")
        table.add_column("Temperature", justify="right")
        table.add_column("Precipitation", justify="right")
        table.add_column("Wind speed", justify="right")
        for forecast in forecasts:
            table.add_row(
                forecast.hour.strftime("%H:%M"),
                WEATHERCODE_DESCRIPTION_MAPPING.get(forecast.weathercode, "-"),
                f"{colorize_temperature(forecast.temperature_celsius)}°C ({colorize_temperature(forecast.apparent_temperature_celsius)}°C)",
                f"{forecast.precipitation_mm}mm",
                f"{forecast.windspeed_meters_per_second}m/s, {get_wind_direction(forecast.wind_direction_degrees)}",
            )
        return table


WEATHERCODE_DESCRIPTION_MAPPING = {
    0: "Clear sky",
    #
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    #
    45: "Fog",
    48: "Fog + rime",
    #
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    #
    56: "Light, freezing drizzle",
    57: "Dense, freezing drizzle",
    #
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    #
    66: "Light, freezing rain",
    67: "Heavy, freezing rain",
    #
    71: "Light snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    #
    77: "Snow grains",
    #
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    #
    85: "Light snow showers",
    86: "Heavy snow showers",
    #
    95: "Thunderstorm",
    #
    96: "Thunderstorm + light hail",
    99: "Thunderstorm + heavy hail",
}


def colorize_temperature(temperature: float) -> str:
    # https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
    if temperature >= 30:
        color = "bright_red"
    elif temperature >= 20:
        color = "dark_orange3"
    elif temperature >= 10:
        color = "yellow3"
    elif temperature >= 0:
        color = "sky_blue1"
    else:
        color = "dodger_blue2"
    return f"[{color}]{temperature}[/]"


def get_wind_direction(
    wind_direction_degrees: float,
) -> str:
    return {
        0: "N",
        1: "NE",
        2: "E",
        3: "SE",
        4: "S",
        5: "SW",
        6: "W",
        7: "NW",
        8: "N",
    }[round((wind_direction_degrees + 360) % 360 / 45)]
