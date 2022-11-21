from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich.padding import Padding


from weatherforecastcli.geocoding import GeocodedLocation
from weatherforecastcli.openmeteo import Forecast, ForecastDay, ForecastHour


def pad_upper(renderable):
    return Padding(renderable, (1, 0, 0, 0))


class SummaryForecastRenderer:
    def render(self, location: GeocodedLocation, forecast: Forecast):
        dates = sorted(forecast.days.keys())
        return Panel(
            Group(
                f"[strong]Weather forecast for\n"
                f"[vstrong]{location.name}, {location.country_name} ({location.latitude}, {location.longitude})[/][/]",
                pad_upper(
                    Columns(
                        [self._render_day(forecast.days[d]) for d in dates],
                        equal=True,
                    )
                ),
            )
        )

    def _render_day(self, forecast: ForecastDay):
        table = Table(show_header=False, show_lines=True, expand=True)
        table.add_column("", justify="left")
        table.add_column("", justify="right")
        table.add_row("", f"[vstrong]{forecast.date.strftime('%A %d %B')}[/]")
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
        location: GeocodedLocation,
        forecast: Forecast,
        resolution_hours: int,
    ):
        dates = sorted(forecast.days.keys())
        return Panel(
            Group(
                f"[strong]Weather forecast for\n"
                f"[vstrong]{location.name}, {location.country_name} ({location.latitude}, {location.longitude})[/][/]",
                pad_upper(
                    Group(
                        *[
                            self._render_day(forecast.days[d], resolution_hours)
                            for d in dates
                        ]
                    )
                ),
            )
        )

    def _render_day(self, forecast: ForecastDay, resolution_hours: int):
        hours = sorted(forecast.hours.keys())
        hours = [h for h in hours if h.hour % resolution_hours == 0]
        return Panel(
            Group(
                f"[vstrong]{forecast.date.strftime('%A %d %B')}[/]",
                pad_upper(
                    Group(
                        f"[vstrong]Summary:\t\t{WEATHERCODE_DESCRIPTION_MAPPING.get(forecast.weathercode, '-')}[/]",
                        f"[strong]Temperature:[/]\t\t{colorize_temperature(forecast.temperature_min_celsius)}/{colorize_temperature(forecast.temperature_max_celsius)}°C "
                        f"({colorize_temperature(forecast.apparent_temperature_min_celsius)}/{colorize_temperature(forecast.apparent_temperature_max_celsius)}°C)",
                        f"[strong]Precipitation:[/]\t\t{forecast.total_precipitation_mm}mm, {round(forecast.total_precipitation_hours)}hr",
                        f"[strong]Wind speed:[/]\t\t{forecast.max_windspeed_meters_per_second}m/s, {get_wind_direction(forecast.dominant_wind_direction_degrees)}",
                        f"[strong]Sunrise/Sunset:[/]\t\t{forecast.sunrise.strftime('%H:%M')}, {forecast.sunset.strftime('%H:%M')}",
                    )
                ),
                pad_upper(self._render_hours([forecast.hours[h] for h in hours])),
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
                f"{forecast.precipitation_mm}mm/h",
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
