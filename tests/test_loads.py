import pytest

from solarwind.loads import Appliance, daily_energy_kwh, energy_breakdown, peak_load_watts, read_loads_csv


def test_daily_energy_adds_up_all_appliances():
    appliances = [Appliance("Bulb", 10, quantity=5, hours_per_day=4), Appliance("Fridge", 100, hours_per_day=24)]
    # 10 W x 5 x 4 h = 200 Wh, plus 100 W x 24 h = 2,400 Wh
    assert daily_energy_kwh(appliances) == pytest.approx(2.6)


def test_peak_load_counts_only_what_runs_together():
    appliances = [Appliance("Kettle", 3000, hours_per_day=0.3), Appliance("Microwave", 900, hours_per_day=0.3, on_at_once=0)]
    assert peak_load_watts(appliances) == 3000


def test_on_at_once_defaults_to_quantity():
    assert Appliance("Bulb", 10, quantity=4, hours_per_day=1).peak_watts == 40


@pytest.mark.parametrize(
    "kwargs",
    [
        {"watts": -1, "hours_per_day": 1},
        {"watts": 10, "hours_per_day": 25},
        {"watts": 10, "hours_per_day": 1, "quantity": 2, "on_at_once": 3},
    ],
)
def test_invalid_appliances_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Appliance("Bad", **kwargs)


def test_read_loads_csv(tmp_path):
    path = tmp_path / "loads.csv"
    path.write_text("name,watts,quantity,hours_per_day,on_at_once\nBulb,8,3,5,\nIron,1000,1,0.5,0\n")
    appliances = read_loads_csv(path)
    assert [a.name for a in appliances] == ["Bulb", "Iron"]
    assert appliances[0].on_at_once == 3
    assert appliances[1].on_at_once == 0


def test_read_loads_csv_reports_the_bad_line(tmp_path):
    path = tmp_path / "loads.csv"
    path.write_text("name,watts,quantity,hours_per_day\nBulb,eight,1,5\n")
    with pytest.raises(ValueError, match="line 2"):
        read_loads_csv(path)


def test_energy_breakdown_is_biggest_first_and_shares_add_up():
    appliances = [Appliance("Bulb", 10, quantity=5, hours_per_day=4), Appliance("Fridge", 100, hours_per_day=24)]
    breakdown = energy_breakdown(appliances)
    assert [a.name for a, _, _ in breakdown] == ["Fridge", "Bulb"]
    assert breakdown[0][1] == pytest.approx(2.4)
    assert breakdown[0][2] == pytest.approx(2.4 / 2.6)
    assert sum(share for _, _, share in breakdown) == pytest.approx(1)


def test_energy_breakdown_with_no_energy_use_does_not_divide_by_zero():
    breakdown = energy_breakdown([Appliance("Spare", 100, quantity=0, hours_per_day=2)])
    assert breakdown[0][1:] == (0, 0)


def test_energy_breakdown_of_nothing_is_empty():
    assert energy_breakdown([]) == []
