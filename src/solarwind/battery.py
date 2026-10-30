"""Battery bank sizing."""


def battery_capacity_kwh(energy_kwh, depth_of_discharge=0.8, efficiency=0.95):
    """Battery size needed to supply energy_kwh without draining it below the safe limit.

    depth_of_discharge: how much of the battery you can safely use
    (about 0.8-0.9 for lithium, 0.5 for lead-acid).
    """
    if not 0 < depth_of_discharge <= 1:
        raise ValueError("Depth of discharge must be between 0 and 1")
    if not 0 < efficiency <= 1:
        raise ValueError("Efficiency must be between 0 and 1")
    return energy_kwh / (depth_of_discharge * efficiency)


def amp_hours(capacity_kwh, system_voltage):
    """Convert a battery capacity in kWh to amp-hours at a system voltage (12, 24 or 48 V)."""
    if system_voltage <= 0:
        raise ValueError("System voltage must be greater than zero")
    return capacity_kwh * 1000 / system_voltage


def suggest_system_voltage(capacity_kwh):
    """Higher voltages keep currents and cable sizes manageable for bigger systems."""
    if capacity_kwh <= 2:
        return 12
    if capacity_kwh <= 6:
        return 24
    return 48
