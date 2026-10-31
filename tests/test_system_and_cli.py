import json
from pathlib import Path

from solarwind.cli import main
from solarwind.loads import read_loads_csv
from solarwind.system import design_system

EXAMPLE = Path(__file__).parent.parent / "examples" / "uk-home.csv"


def test_wind_reduces_the_solar_needed():
    appliances = read_loads_csv(EXAMPLE)
    solar_only = design_system(appliances, "manchester")
    with_wind = design_system(appliances, "manchester", turbine={"mean_speed": 5.5, "rated_watts": 1000, "rated_speed": 11})
    assert with_wind.solar_panels < solar_only.solar_panels


def test_no_panels_when_wind_covers_everything():
    appliances = read_loads_csv(EXAMPLE)
    design = design_system(appliances, "london", turbine={"mean_speed": 8, "rated_watts": 3000, "rated_speed": 11})
    assert design.solar_panels == 0


def test_tiny_winter_shortfall_is_ignored():
    appliances = read_loads_csv(Path(__file__).parent.parent / "examples" / "off-grid-cabin.csv")
    design = design_system(appliances, "edinburgh", turbine={"mean_speed": 6, "rated_watts": 400, "rated_speed": 12})
    assert design.winter_shortfall_kwh == 0


def test_cli_system_json(capsys):
    assert main(["system", "--loads", str(EXAMPLE), "--location", "london", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["solar_panels"] > 0
    assert result["inverter_kva"] >= 3


def test_cli_wind_text(capsys):
    assert main(["wind", "--mean-speed", "5", "--rated-watts", "1000", "--rated-speed", "11"]) == 0
    assert "Output per year" in capsys.readouterr().out


def test_cli_solar_markdown(capsys):
    assert main(["solar", "--daily-kwh", "8", "--sun-hours", "3.2", "--markdown"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("## Solar array\n")
    assert "| Item | Value |" in output
    assert "| Energy needed per day | 8.0 kWh |" in output


def test_cli_wind_markdown_includes_low_wind_note(capsys):
    assert main(["wind", "--mean-speed", "4", "--rated-watts", "1000", "--rated-speed", "11", "--markdown"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("## Wind turbine\n")
    assert "| Note | Sites averaging under about 4.5 m/s rarely make a turbine worthwhile. |" in output


def test_cli_system_markdown(capsys):
    assert main(["system", "--loads", str(EXAMPLE), "--location", "london", "--markdown"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("## System for London\n")
    assert "| Appliances |" in output
    assert "| Solar array |" in output


def test_cli_reports_missing_file(capsys):
    assert main(["system", "--loads", "missing.csv"]) == 1
    assert "error:" in capsys.readouterr().err
