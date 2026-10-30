"""Small wind turbine output estimates.

Wind speed varies all the time, so we combine the turbine's power curve with a
Rayleigh distribution of wind speeds, the standard approach when you only know
a site's average wind speed.
"""

import math

HOURS_PER_YEAR = 8760

# Real small turbines produce less than their published power curve suggests,
# because of turbulence, yawing, downtime and wiring losses. UK field trials
# found large shortfalls on poor sites, so we take a quarter off by default.
DEFAULT_LOSSES = 0.25

# Wind shear exponents: how quickly wind speed rises with height over different ground.
TERRAIN_SHEAR = {
    "water": 0.10,      # sea, lakes
    "open": 0.14,       # open fields, coast, moorland
    "rural": 0.20,      # farmland with hedges and scattered trees
    "suburban": 0.30,   # villages, suburbs, woodland edges
    "urban": 0.40,      # town and city centres
}


def wind_speed_at_height(speed, measured_height, hub_height, terrain="open"):
    """Estimate wind speed at the turbine's hub height from a measurement at another height."""
    if measured_height <= 0 or hub_height <= 0:
        raise ValueError("Heights must be greater than zero")
    if terrain not in TERRAIN_SHEAR:
        raise ValueError(f"Terrain must be one of: {', '.join(TERRAIN_SHEAR)}")
    return speed * (hub_height / measured_height) ** TERRAIN_SHEAR[terrain]


def power_at_speed(speed, rated_watts, rated_speed, cut_in=2.5, cut_out=25.0):
    """Turbine output (watts) at one wind speed, using a simple cubic power curve."""
    if speed < cut_in or speed >= cut_out:
        return 0.0
    if speed >= rated_speed:
        return float(rated_watts)
    return rated_watts * (speed**3 - cut_in**3) / (rated_speed**3 - cut_in**3)


def rayleigh_probability(speed, mean_speed):
    """How often the wind blows at a given speed, for a site with this average speed."""
    if speed < 0:
        return 0.0
    return (math.pi / 2) * (speed / mean_speed**2) * math.exp(-(math.pi / 4) * (speed / mean_speed) ** 2)


def annual_energy_kwh(mean_speed, rated_watts, rated_speed, cut_in=2.5, cut_out=25.0, losses=DEFAULT_LOSSES, step=0.1):
    """Estimated energy per year (kWh) at a site with the given average wind speed at hub height."""
    if mean_speed <= 0:
        raise ValueError("Average wind speed must be greater than zero")
    if not 0 <= losses < 1:
        raise ValueError("Losses must be between 0 and 1")
    average_watts = 0.0
    speed = step / 2
    while speed < 40:
        average_watts += power_at_speed(speed, rated_watts, rated_speed, cut_in, cut_out) * rayleigh_probability(speed, mean_speed) * step
        speed += step
    return average_watts * (1 - losses) * HOURS_PER_YEAR / 1000


def capacity_factor(annual_kwh, rated_watts):
    """Share of the year's maximum possible output that the turbine actually produces."""
    return annual_kwh / (rated_watts / 1000 * HOURS_PER_YEAR)
