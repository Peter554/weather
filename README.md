# weather

A little weather CLI using [Positionstack](https://positionstack.com/) for geocoding 
and [Meteomatics](https://www.meteomatics.com/) for weather data.

Just a small hacking project. Missing tests, limited error handling, no CI, not published to PyPI etc... 
Just for fun!

## Usage

* Create a free account on both Positionstack & Meteomatics.
* Install [Poetry](https://python-poetry.org/) (I haven't published to PyPI, just hacking).
* Clone this repo.
* Install the CLI: `poetry install`
* Initialize the CLI: `poetry run weather init`
* Start getting weather forecasts!

### Forecasts

```
❯ poetry run weather forecast --help
                                                                                                
 Usage: weather forecast [OPTIONS] LOCATION                                                     
                                                                                                
 Fetch and display a weather forecast.                                                          
                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────╮
│ *    location      TEXT  [default: None] [required]                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --skip-days         INTEGER               [default: 0]                                       │
│ --take-days         INTEGER               [default: 2]                                       │
│ --resolution        [1H|2H|3H|4H|6H|12H]  [default: ForcastResolution.THREE_HOUR]            │
│ --help                                    Show this message and exit.                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

example:

```
❯ poetry run weather forecast "Glasgow UK" 
Forcast for Glasgow GBR ((55.8608, -4.2682))
                                        2022-11-18                                        
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃        Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 18:00:00 │ Cloudy (night) │              7.0 │              5.1 │                  0.0 │
│ 21:00:00 │ Cloudy (night) │              7.0 │              2.5 │                  0.0 │
└──────────┴────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                           2022-11-19                                            
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃               Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │ Partly cloudy (night) │              6.3 │              1.8 │                  0.0 │
│ 03:00:00 │        Cloudy (night) │              5.6 │              1.8 │                  0.0 │
│ 06:00:00 │        Cloudy (night) │              6.2 │              0.6 │                  0.0 │
│ 09:00:00 │                Cloudy │              6.4 │              0.9 │                  0.0 │
│ 12:00:00 │         Partly cloudy │              8.4 │              1.5 │                  0.0 │
│ 15:00:00 │         Partly cloudy │              8.2 │              2.0 │                  0.0 │
│ 18:00:00 │        Cloudy (night) │              6.1 │              3.0 │                  0.0 │
│ 21:00:00 │          Rain (night) │              7.0 │              4.3 │                 0.38 │
└──────────┴───────────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```

one more example:

```
❯ poetry run weather forecast "Berkeley US" --skip-days 1 --take-days 3 --resolution 4H

Forcast for Berkeley USA ((37.8658, -122.2979))
                                         2022-11-19                                          
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃           Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │ Clear sky (night) │              9.6 │              4.1 │                  0.0 │
│ 04:00:00 │ Clear sky (night) │              8.1 │              4.7 │                  0.0 │
│ 08:00:00 │         Clear sky │              9.5 │              5.6 │                  0.0 │
│ 12:00:00 │         Clear sky │             16.2 │              4.1 │                  0.0 │
│ 16:00:00 │         Clear sky │             15.7 │              3.6 │                  0.0 │
│ 20:00:00 │ Clear sky (night) │             10.4 │              2.7 │                  0.0 │
└──────────┴───────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                           2022-11-20                                           
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃              Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │    Clear sky (night) │              8.7 │              3.0 │                  0.0 │
│ 04:00:00 │ Light clouds (night) │              8.7 │              3.7 │                  0.0 │
│ 08:00:00 │         Light clouds │             10.6 │              3.7 │                  0.0 │
│ 12:00:00 │         Light clouds │             16.6 │              3.0 │                  0.0 │
│ 16:00:00 │            Clear sky │             16.0 │              2.8 │                  0.0 │
│ 20:00:00 │    Clear sky (night) │             10.1 │              3.0 │                  0.0 │
└──────────┴──────────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                           2022-11-21                                           
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃              Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │    Clear sky (night) │              8.4 │              2.9 │                  0.0 │
│ 04:00:00 │    Clear sky (night) │              7.4 │              2.9 │                  0.0 │
│ 08:00:00 │            Clear sky │             10.2 │              2.5 │                  0.0 │
│ 12:00:00 │         Light clouds │             16.7 │              2.2 │                  0.0 │
│ 16:00:00 │            Clear sky │             16.1 │              2.4 │                  0.0 │
│ 20:00:00 │ Light clouds (night) │             10.6 │              2.8 │                  0.0 │
└──────────┴──────────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```
