# solarwind

**Size solar panels, small wind turbines, batteries and inverters for homes and small businesses.** It's a command-line tool and Python library with no dependencies.

Tell it what appliances you want to run and where you live, and it estimates:

- how much energy you use per day and your peak load
- the inverter size you need
- the battery bank (kWh and amp-hours)
- how much a wind turbine would produce at your site
- how many solar panels cover the rest, and how short you'd fall in the darkest month

```
$ solarwind system --loads examples/uk-home.csv --location manchester --wind-speed 5.5

System for Manchester
---------------------
Appliances      9 types
Energy per day  5.0 kWh
Peak load       3,396 W
Inverter        6 kVA
Battery         4.0 kWh (165 Ah at 24 V)
Wind (average)  3.7 kWh/day
Solar needed    1.3 kWh/day
Solar array     0.62 kW (2 x 450 W)

In the darkest month you may be short by about 0.9 kWh/day: plan for grid backup, a generator or more panels.
```

> ⚠️ **These are estimates for planning, not a substitute for a professional site survey.** Real output depends on shading, roof direction, local wind conditions and equipment quality.

## Install

You need Python 3.9 or newer.

```bash
git clone https://github.com/snok-dev/solar-wind-sizer.git
cd solar-wind-sizer
python3 -m pip install .
```

## Usage

### Size a whole system from your appliances

List your appliances in a CSV file (see [`examples/`](examples)):

```csv
name,watts,quantity,hours_per_day,on_at_once
LED bulb,8,12,5,
Kettle,3000,1,0.3,
Microwave,900,1,0.3,0
```

`on_at_once` is how many can run at the same moment. Leave it blank for all of them, or use `0` for something you'd never run alongside the big loads. It keeps the inverter from being oversized.

```bash
solarwind system --loads examples/uk-home.csv --location london
solarwind system --loads examples/off-grid-cabin.csv --location edinburgh --wind-speed 6 --turbine-watts 400 --turbine-rated-speed 12
```

### Size a solar array

```bash
solarwind solar --daily-kwh 8 --location london              # average day
solarwind solar --daily-kwh 8 --location london --season low  # darkest month
solarwind solar --daily-kwh 8 --sun-hours 3.2                # your own figure
```

Built-in locations: London, Cardiff, Manchester, Belfast, Edinburgh, Lagos, Abuja.

### Estimate a wind turbine's output

```bash
solarwind wind --mean-speed 5 --rated-watts 1000 --rated-speed 11

# Measured 4.5 m/s on a 2 m pole, turbine hub at 10 m, farmland with hedges:
solarwind wind --mean-speed 4.5 --measured-height 2 --hub-height 10 --terrain rural --rated-watts 1000 --rated-speed 11
```

Add `--json` to any command for machine-readable output, or `--markdown` for a paste-ready table:

```bash
solarwind solar --daily-kwh 8 --location london --markdown
```

### As a Python library

```python
from solarwind import wind, solar

kwh = wind.annual_energy_kwh(mean_speed=5.5, rated_watts=1000, rated_speed=11)
panels = solar.panels_needed(solar.array_size_kw(6, solar.peak_sun_hours("cardiff")), 450)
```

## How it works

| Part | Method |
|---|---|
| Solar | Array kW = daily kWh ÷ (peak sun hours × 0.8 performance ratio) |
| Wind speed with height | Power law with a terrain-dependent shear exponent |
| Wind output | Simple cubic power curve × Rayleigh wind-speed distribution, minus 25% real-world losses |
| Battery | Night-time energy ÷ (depth of discharge × efficiency) |
| Inverter | Peak load × 1.25 headroom ÷ 0.8 power factor, rounded up to a standard size |

Peak sun hours are approximate guides for a south-facing panel. See [`src/solarwind/solar.py`](src/solarwind/solar.py).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features. Contributions welcome!

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: open an issue, work on a branch, add tests, and open a pull request.

## Licence

[MIT](LICENSE)
