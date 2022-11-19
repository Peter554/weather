# weather

A little weather CLI using [Positionstack](https://positionstack.com/) for geocoding 
and [Open-Meteo](https://open-meteo.com/) for weather data.

A small hacking project. Missing tests, limited error handling, no CI etc... 
Just for fun!

## Usage

Requires Python 3.10+.

* Create a free account Positionstack.
* Install the CLI: `pip install weatherforecastcli`
* Initialize the CLI: `weather init`
* Start getting weather forecasts!

## Forecast

```
weather forecast --help
```

Summary forecast:

```
weather forecast "Death Valley"
```

![](/usage.svg)

Detailed forecast:

```
weather forecast "Death Valley" --resolution 3H
```

![](/usage-detailed.svg)


