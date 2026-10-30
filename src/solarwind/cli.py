"""Command-line interface: `solarwind solar ...`, `solarwind wind ...`, `solarwind system ...`."""

import argparse
import json
import sys

from . import __version__, battery, loads, solar, wind
from .system import design_system


def print_rows(title, rows):
    """Print a simple two-column report."""
    print(title)
    print("-" * len(title))
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"{label.ljust(width)}  {value}")


def run_solar(args):
    sun_hours = args.sun_hours or solar.peak_sun_hours(args.location, args.season)
    array_kw = solar.array_size_kw(args.daily_kwh, sun_hours)
    panels = solar.panels_needed(array_kw, args.panel_watts)
    result = {
        "daily_kwh": args.daily_kwh,
        "peak_sun_hours": sun_hours,
        "array_kw": round(array_kw, 2),
        "panels": panels,
        "panel_watts": args.panel_watts,
        "annual_kwh": round(solar.annual_output_kwh(panels * args.panel_watts / 1000, sun_hours)),
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print_rows(
        "Solar array",
        [
            ("Energy needed per day", f"{args.daily_kwh:.1f} kWh"),
            ("Peak sun hours", f"{sun_hours} h/day"),
            ("Array size", f"{array_kw:.2f} kW"),
            ("Panels", f"{panels} x {args.panel_watts} W"),
            ("Output per year", f"about {result['annual_kwh']:,} kWh"),
        ],
    )


def run_wind(args):
    mean_speed = args.mean_speed
    if args.measured_height and args.hub_height:
        mean_speed = wind.wind_speed_at_height(mean_speed, args.measured_height, args.hub_height, args.terrain)
    kwh = wind.annual_energy_kwh(mean_speed, args.rated_watts, args.rated_speed, args.cut_in, args.cut_out, args.losses)
    result = {
        "mean_speed_at_hub": round(mean_speed, 2),
        "annual_kwh": round(kwh),
        "daily_kwh": round(kwh / 365, 2),
        "capacity_factor": round(wind.capacity_factor(kwh, args.rated_watts), 3),
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print_rows(
        "Wind turbine",
        [
            ("Average wind at hub", f"{mean_speed:.1f} m/s"),
            ("Turbine", f"{args.rated_watts:,.0f} W rated at {args.rated_speed} m/s"),
            ("Output per year", f"about {result['annual_kwh']:,} kWh"),
            ("Average per day", f"{result['daily_kwh']} kWh"),
            ("Capacity factor", f"{result['capacity_factor'] * 100:.0f}%"),
        ],
    )
    if mean_speed < 4.5:
        print("\nNote: sites averaging under about 4.5 m/s rarely make a turbine worthwhile.")


def run_system(args):
    appliances = loads.read_loads_csv(args.loads)
    turbine = None
    if args.wind_speed:
        turbine = {"mean_speed": args.wind_speed, "rated_watts": args.turbine_watts, "rated_speed": args.turbine_rated_speed}
    design = design_system(
        appliances,
        args.location,
        panel_watts=args.panel_watts,
        night_fraction=args.night_fraction,
        depth_of_discharge=args.dod,
        turbine=turbine,
    )
    if args.json:
        print(json.dumps({k: round(v, 2) if isinstance(v, float) else v for k, v in design.to_dict().items()}, indent=2))
        return
    rows = [
        ("Appliances", f"{len(appliances)} types"),
        ("Energy per day", f"{design.daily_kwh:.1f} kWh"),
        ("Peak load", f"{design.peak_watts:,.0f} W"),
        ("Inverter", f"{design.inverter_kva} kVA" if design.inverter_kva else f"{design.inverter_kva_needed:.1f} kVA+ (larger than standard sizes)"),
        ("Battery", f"{design.battery_kwh:.1f} kWh ({design.battery_ah:.0f} Ah at {design.battery_voltage} V)"),
    ]
    if turbine:
        rows.append(("Wind (average)", f"{design.wind_daily_kwh:.1f} kWh/day"))
    rows += [
        ("Solar needed", f"{design.solar_daily_kwh:.1f} kWh/day"),
        ("Solar array", f"{design.solar_array_kw:.2f} kW ({design.solar_panels} x {args.panel_watts} W)"),
    ]
    print_rows(f"System for {args.location.title()}", rows)
    if design.winter_shortfall_kwh > 0:
        print(f"\nIn the darkest month you may be short by about {design.winter_shortfall_kwh:.1f} kWh/day:"
              " plan for grid backup, a generator or more panels.")


def build_parser():
    parser = argparse.ArgumentParser(prog="solarwind", description="Size solar, wind and battery systems.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("solar", help="size a solar array for a daily energy need")
    p.add_argument("--daily-kwh", type=float, required=True, help="energy needed per day, in kWh")
    p.add_argument("--location", default="london", choices=sorted(solar.LOCATIONS))
    p.add_argument("--season", default="annual", choices=["annual", "low", "high"], help="size for the average, worst or best month")
    p.add_argument("--sun-hours", type=float, help="your own peak sun hours (overrides --location)")
    p.add_argument("--panel-watts", type=float, default=450)
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    p.set_defaults(func=run_solar)

    p = sub.add_parser("wind", help="estimate a wind turbine's yearly output")
    p.add_argument("--mean-speed", type=float, required=True, help="average wind speed in m/s")
    p.add_argument("--rated-watts", type=float, required=True)
    p.add_argument("--rated-speed", type=float, required=True, help="wind speed (m/s) at which the turbine reaches its rated power")
    p.add_argument("--cut-in", type=float, default=2.5)
    p.add_argument("--cut-out", type=float, default=25.0)
    p.add_argument("--losses", type=float, default=wind.DEFAULT_LOSSES, help="real-world losses (0-1), default 0.25")
    p.add_argument("--measured-height", type=float, help="height (m) where the wind speed was measured")
    p.add_argument("--hub-height", type=float, help="height (m) of the turbine hub")
    p.add_argument("--terrain", default="open", choices=list(wind.TERRAIN_SHEAR))
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=run_wind)

    p = sub.add_parser("system", help="size a full system from a CSV of appliances")
    p.add_argument("--loads", required=True, help="CSV file with name, watts, quantity, hours_per_day")
    p.add_argument("--location", default="london", choices=sorted(solar.LOCATIONS))
    p.add_argument("--panel-watts", type=float, default=450)
    p.add_argument("--night-fraction", type=float, default=0.6, help="share of daily energy used after dark (0-1)")
    p.add_argument("--dod", type=float, default=0.8, help="battery depth of discharge (0-1)")
    p.add_argument("--wind-speed", type=float, help="average wind speed at hub height, to include a turbine")
    p.add_argument("--turbine-watts", type=float, default=1000)
    p.add_argument("--turbine-rated-speed", type=float, default=11)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=run_system)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
