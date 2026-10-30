import pytest

from solarwind import wind


def test_no_power_below_cut_in_or_above_cut_out():
    assert wind.power_at_speed(2.0, 1000, 11) == 0
    assert wind.power_at_speed(26, 1000, 11) == 0


def test_rated_power_between_rated_speed_and_cut_out():
    assert wind.power_at_speed(11, 1000, 11) == 1000
    assert wind.power_at_speed(20, 1000, 11) == 1000


def test_power_rises_with_wind_speed():
    speeds = [3, 5, 7, 9]
    powers = [wind.power_at_speed(s, 1000, 11) for s in speeds]
    assert powers == sorted(powers)


def test_rayleigh_probabilities_add_up_to_one():
    total = sum(wind.rayleigh_probability(v / 10 + 0.05, 5.0) * 0.1 for v in range(400))
    assert total == pytest.approx(1.0, abs=0.01)


def test_annual_energy_for_a_1kw_turbine_on_a_good_site():
    kwh = wind.annual_energy_kwh(mean_speed=5.0, rated_watts=1000, rated_speed=11)
    # Real 1 kW turbines on decent UK sites produce roughly 800-2,000 kWh a year
    assert 800 <= kwh <= 2000


def test_more_wind_means_much_more_energy():
    calm = wind.annual_energy_kwh(4.0, 1000, 11)
    windy = wind.annual_energy_kwh(6.0, 1000, 11)
    assert windy > calm * 2


def test_losses_reduce_output():
    ideal = wind.annual_energy_kwh(5.0, 1000, 11, losses=0)
    real = wind.annual_energy_kwh(5.0, 1000, 11, losses=0.25)
    assert real == pytest.approx(ideal * 0.75)


def test_wind_is_faster_higher_up():
    assert wind.wind_speed_at_height(5.0, 10, 20, "open") > 5.0
    assert wind.wind_speed_at_height(5.0, 10, 10, "urban") == pytest.approx(5.0)


def test_capacity_factor():
    assert wind.capacity_factor(876, 1000) == pytest.approx(0.1)
