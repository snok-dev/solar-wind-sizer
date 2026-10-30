import pytest

from solarwind import solar


def test_array_size():
    # 8 kWh a day with 4 sun hours at 80% performance needs a 2.5 kW array
    assert solar.array_size_kw(8, 4) == pytest.approx(2.5)


def test_panels_needed_rounds_up():
    assert solar.panels_needed(2.5, 450) == 6  # 5.56 panels -> 6


def test_annual_output_for_london_is_realistic():
    # UK installers usually quote 800-950 kWh per year for each kW of panels in the south
    kwh = solar.annual_output_kwh(1, solar.peak_sun_hours("London"))
    assert 800 <= kwh <= 950


def test_winter_needs_more_panels_than_summer():
    winter = solar.array_size_kw(5, solar.peak_sun_hours("edinburgh", "low"))
    summer = solar.array_size_kw(5, solar.peak_sun_hours("edinburgh", "high"))
    assert winter > summer * 5


def test_unknown_location_lists_known_ones():
    with pytest.raises(ValueError, match="london"):
        solar.peak_sun_hours("Atlantis")


def test_zero_sun_hours_is_rejected():
    with pytest.raises(ValueError):
        solar.array_size_kw(5, 0)
