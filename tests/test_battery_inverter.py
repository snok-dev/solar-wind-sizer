import pytest

from solarwind import battery, inverter


def test_battery_capacity_allows_for_depth_of_discharge():
    assert battery.battery_capacity_kwh(4, depth_of_discharge=0.8, efficiency=1) == pytest.approx(5)


def test_amp_hours():
    assert battery.amp_hours(4.8, 48) == pytest.approx(100)


@pytest.mark.parametrize("kwh, volts", [(1.5, 12), (4, 24), (10, 48)])
def test_suggested_voltage_rises_with_size(kwh, volts):
    assert battery.suggest_system_voltage(kwh) == volts


def test_required_kva_includes_headroom():
    # 2,000 W x 1.25 headroom / 0.8 power factor = 3.125 kVA
    assert inverter.required_kva(2000) == pytest.approx(3.125)


def test_standard_size_rounds_up():
    assert inverter.standard_inverter_kva(3.125) == 3.5
    assert inverter.standard_inverter_kva(99) is None


def test_energy_to_store_uses_night_fraction_by_default():
    assert battery.energy_to_store_kwh(10) == pytest.approx(6)


def test_energy_to_store_for_autonomy_days():
    assert battery.energy_to_store_kwh(10, autonomy_days=3) == pytest.approx(30)


def test_autonomy_days_must_be_positive():
    with pytest.raises(ValueError):
        battery.energy_to_store_kwh(10, autonomy_days=0)
        