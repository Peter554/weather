# weather

A little weather CLI using [Positionstack](https://positionstack.com/) for geocoding 
and [Meteomatics](https://www.meteomatics.com/) for weather data.

Just a small hacking project. Missing tests, limited error handling, no CI etc... 
Just for fun!

## Usage

Requires Python 3.10+.

* Create a free account on both Positionstack & Meteomatics.
* Install the CLI: `pip install weatherforecastcli`
* Initialize the CLI: `weather init`
* Start getting weather forecasts!

### Forecasts

```
❯ weather forecast --help
                                                                                                
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
❯  weather forecast "Glasgow UK" 
Forcast for Glasgow GBR ((55.8608, -4.2682))
                                           2022-11-18                                            
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃               Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 21:00:00 │ Partly cloudy (night) │              6.7 │           3.5 SW │                 0.03 │
└──────────┴───────────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                         2022-11-19                                          
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃           Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │    Cloudy (night) │              6.7 │           1.7  W │                  0.0 │
│ 03:00:00 │    Cloudy (night) │              8.0 │           2.3  W │                  0.0 │
│ 06:00:00 │ Clear sky (night) │              4.9 │           2.0  S │                  0.0 │
│ 09:00:00 │            Cloudy │              5.1 │           1.4  S │                  0.0 │
│ 12:00:00 │     Partly cloudy │              8.7 │           1.9 SE │                  0.0 │
│ 15:00:00 │     Partly cloudy │              8.7 │           2.9  S │                  0.0 │
│ 18:00:00 │    Cloudy (night) │              6.7 │           3.2 SE │                  0.0 │
│ 21:00:00 │      Rain (night) │              7.4 │           4.5 SE │                 0.38 │
└──────────┴───────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```

one more example:

```
❯ weather forecast "Berkeley US" --skip-days 1 --take-days 3 --resolution 4H
Forcast for Berkeley USA ((37.8658, -122.2979))
                                         2022-11-19                                          
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃           Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │ Clear sky (night) │              9.5 │           3.8 NE │                  0.0 │
│ 04:00:00 │ Clear sky (night) │              8.1 │           5.0 NE │                  0.0 │
│ 08:00:00 │         Clear sky │              9.5 │           5.8 NE │                  0.0 │
│ 12:00:00 │         Clear sky │             16.0 │           3.7 NE │                  0.0 │
│ 16:00:00 │         Clear sky │             15.6 │           3.3 NE │                  0.0 │
│ 20:00:00 │ Clear sky (night) │             10.0 │           2.4 NE │                  0.0 │
└──────────┴───────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                         2022-11-20                                          
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃           Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │ Clear sky (night) │              8.3 │           3.0 NE │                  0.0 │
│ 04:00:00 │ Clear sky (night) │              8.0 │           3.7 NE │                  0.0 │
│ 08:00:00 │         Clear sky │             10.7 │           3.8 NE │                  0.0 │
│ 12:00:00 │         Clear sky │             16.9 │           2.9 NE │                  0.0 │
│ 16:00:00 │         Clear sky │             16.0 │           3.0  N │                  0.0 │
│ 20:00:00 │ Clear sky (night) │             10.2 │           2.9 NE │                  0.0 │
└──────────┴───────────────────┴──────────────────┴──────────────────┴──────────────────────┘
                                           2022-11-21                                           
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time     ┃              Summary ┃ Temperature (°C) ┃ Wind speed (m/s) ┃ Precipitation (mm/h) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 00:00:00 │    Clear sky (night) │              8.3 │           2.7 NE │                  0.0 │
│ 04:00:00 │    Clear sky (night) │              7.4 │           2.7 NE │                  0.0 │
│ 08:00:00 │         Light clouds │             10.3 │           2.5 NE │                  0.0 │
│ 12:00:00 │         Light clouds │             16.7 │           2.2  N │                  0.0 │
│ 16:00:00 │            Clear sky │             16.1 │           2.4  N │                  0.0 │
│ 20:00:00 │ Light clouds (night) │             10.6 │           2.8  N │                  0.0 │
└──────────┴──────────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```
