import pytest

from solarwind.loads import Appliance, daily_energy_kwh, peak_load_watts, read_loads_csv


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
