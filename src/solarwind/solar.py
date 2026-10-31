"""Solar panel sizing.

Peak sun hours (PSH) are the number of hours per day of full-strength sunshine
(1,000 W/m2) that would deliver the same energy as the real day's sunshine.
"""

import math

# Approximate peak sun hours for a south-facing panel at a typical tilt.
# "low" is the worst month (usually December), "high" the best (usually June).
# These are rough guides only: use measured data for a real installation.
LOCATIONS = {
    "london": {"annual": 2.9, "low": 0.8, "high": 5.0},
    "cardiff": {"annual": 3.0, "low": 0.9, "high": 5.1},
    "manchester": {"annual": 2.6, "low": 0.6, "high": 4.6},
    "birmingham": {"annual": 2.7, "low": 0.7, "high": 4.9},
    "bristol": {"annual": 2.9, "low": 0.8, "high": 5.0},
    "newcastle": {"annual": 2.5, "low": 0.5, "high": 4.6},
    "belfast": {"annual": 2.5, "low": 0.5, "high": 4.5},
    "edinburgh": {"annual": 2.5, "low": 0.4, "high": 4.6},
    "glasgow": {"annual": 2.4, "low": 0.4, "high": 4.5},
    "lagos": {"annual": 4.6, "low": 3.5, "high": 5.5},
    "abuja": {"annual": 5.5, "low": 4.4, "high": 6.4},
    "portharcourt": {"annual": 4.2, "low": 3.4, "high": 5.2},
    "kano": {"annual": 5.8, "low": 4.6, "high": 6.6},
}

# Share of the panels' rated output that reaches your sockets after losses
# from heat, dirt, wiring and the inverter.
DEFAULT_PERFORMANCE_RATIO = 0.8


def peak_sun_hours(location, season="annual"):
    """Look up peak sun hours for a known location and season."""
    key = location.lower()
    if key not in LOCATIONS:
        known = ", ".join(sorted(LOCATIONS))
        raise ValueError(f"Unknown location '{location}'. Known locations: {known}")
    if season not in LOCATIONS[key]:
        raise ValueError("Season must be 'annual', 'low' or 'high'")
    return LOCATIONS[key][season]


def array_size_kw(daily_kwh, sun_hours, performance_ratio=DEFAULT_PERFORMANCE_RATIO):
    """Solar array size (kW peak) needed to produce daily_kwh on an average day."""
    if sun_hours <= 0:
        raise ValueError("Peak sun hours must be greater than zero")
    return daily_kwh / (sun_hours * performance_ratio)


def panels_needed(array_kw, panel_watts):
    """Number of panels of a given wattage to reach an array size."""
    if panel_watts <= 0:
        raise ValueError("Panel watts must be greater than zero")
    return math.ceil(array_kw * 1000 / panel_watts)


def daily_output_kwh(array_kw, sun_hours, performance_ratio=DEFAULT_PERFORMANCE_RATIO):
    """Average energy an array produces per day."""
    return array_kw * sun_hours * performance_ratio


def annual_output_kwh(array_kw, sun_hours, performance_ratio=DEFAULT_PERFORMANCE_RATIO):
    """Energy an array produces in a year, using the annual average sun hours."""
    return daily_output_kwh(array_kw, sun_hours, performance_ratio) * 365
