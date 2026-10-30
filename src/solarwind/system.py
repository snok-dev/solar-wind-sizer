"""Size a complete system from a list of loads, combining solar, wind and batteries."""

from dataclasses import asdict, dataclass

from . import battery, inverter, loads, solar, wind


@dataclass
class SystemDesign:
    daily_kwh: float
    peak_watts: float
    inverter_kva_needed: float
    inverter_kva: float
    battery_kwh: float
    battery_voltage: int
    battery_ah: float
    wind_daily_kwh: float
    solar_daily_kwh: float
    solar_array_kw: float
    solar_panels: int
    winter_shortfall_kwh: float

    def to_dict(self):
        return asdict(self)


def design_system(
    appliances,
    location,
    panel_watts=450,
    night_fraction=0.6,
    depth_of_discharge=0.8,
    turbine=None,
):
    """Work out inverter, battery, wind and solar sizes for a set of appliances.

    night_fraction: share of daily energy used when the sun isn't shining,
    which the battery has to store.
    turbine: optional dict with mean_speed, rated_watts and rated_speed (plus
    optional cut_in and cut_out) for a wind turbine at the site.
    """
    daily = loads.daily_energy_kwh(appliances)
    peak = loads.peak_load_watts(appliances)

    kva_needed = inverter.required_kva(peak)
    kva = inverter.standard_inverter_kva(kva_needed)

    battery_kwh = battery.battery_capacity_kwh(daily * night_fraction, depth_of_discharge)
    voltage = battery.suggest_system_voltage(battery_kwh)

    wind_daily = 0.0
    if turbine:
        wind_daily = wind.annual_energy_kwh(**turbine) / 365

    # Solar covers whatever wind doesn't, on an average day
    # (anything under 50 Wh a day is rounding noise, not a real need for panels)
    solar_daily = max(0.0, daily - wind_daily)
    if solar_daily < 0.05:
        solar_daily = 0.0
    array_kw = solar.array_size_kw(solar_daily, solar.peak_sun_hours(location))
    panels = solar.panels_needed(array_kw, panel_watts) if solar_daily > 0 else 0

    # How short the system falls on a typical day in the darkest month.
    # Wind is counted at its yearly average, which is cautious: UK winters are windier.
    winter_output = solar.daily_output_kwh(panels * panel_watts / 1000, solar.peak_sun_hours(location, "low"))
    shortfall = max(0.0, daily - wind_daily - winter_output)
    if shortfall < 0.05:
        shortfall = 0.0

    return SystemDesign(
        daily_kwh=daily,
        peak_watts=peak,
        inverter_kva_needed=kva_needed,
        inverter_kva=kva,
        battery_kwh=battery_kwh,
        battery_voltage=voltage,
        battery_ah=battery.amp_hours(battery_kwh, voltage),
        wind_daily_kwh=wind_daily,
        solar_daily_kwh=solar_daily,
        solar_array_kw=array_kw,
        solar_panels=panels,
        winter_shortfall_kwh=shortfall,
    )
