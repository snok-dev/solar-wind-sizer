"""Electrical loads: the appliances a system has to power."""

import csv
from dataclasses import dataclass
from typing import Optional


@dataclass
class Appliance:
    """One kind of appliance, e.g. 10 LED bulbs used 6 hours a day.

    on_at_once: how many of them can be running at the same moment
    (defaults to all of them). Used for the peak load.
    """

    name: str
    watts: float
    quantity: int = 1
    hours_per_day: float = 0.0
    on_at_once: Optional[int] = None

    def __post_init__(self):
        if self.watts < 0:
            raise ValueError(f"{self.name}: watts cannot be negative")
        if self.quantity < 0:
            raise ValueError(f"{self.name}: quantity cannot be negative")
        if not 0 <= self.hours_per_day <= 24:
            raise ValueError(f"{self.name}: hours per day must be between 0 and 24")
        if self.on_at_once is None:
            self.on_at_once = self.quantity
        if not 0 <= self.on_at_once <= self.quantity:
            raise ValueError(f"{self.name}: on_at_once must be between 0 and quantity")

    @property
    def total_watts(self):
        """Power drawn when all of them are on."""
        return self.watts * self.quantity

    @property
    def peak_watts(self):
        """Power drawn when the most that can run together are on."""
        return self.watts * self.on_at_once

    @property
    def daily_wh(self):
        """Energy used per day, in watt-hours."""
        return self.total_watts * self.hours_per_day


def peak_load_watts(appliances):
    """Highest power drawn at one moment, counting only what can run together."""
    return sum(a.peak_watts for a in appliances)


def daily_energy_kwh(appliances):
    """Total energy used per day, in kilowatt-hours."""
    return sum(a.daily_wh for a in appliances) / 1000


def read_loads_csv(path):
    """Read appliances from a CSV file.

    Columns: name, watts, quantity, hours_per_day, and optionally on_at_once
    (leave it blank to count all of them in the peak load).
    """
    appliances = []
    with open(path, newline="", encoding="utf-8") as f:
        for line_number, row in enumerate(csv.DictReader(f), start=2):
            try:
                appliances.append(
                    Appliance(
                        name=row["name"].strip(),
                        watts=float(row["watts"]),
                        quantity=int(row.get("quantity") or 1),
                        hours_per_day=float(row["hours_per_day"]),
                        on_at_once=int(row["on_at_once"]) if (row.get("on_at_once") or "").strip() else None,
                    )
                )
            except (KeyError, ValueError) as error:
                raise ValueError(f"{path}, line {line_number}: {error}") from error
    return appliances
