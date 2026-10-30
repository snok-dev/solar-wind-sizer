# Roadmap

Planned work, roughly from easiest to hardest. Each item is (or will be) a GitHub issue.

## Good first issues
- [ ] **More locations:** add Birmingham, Bristol, Glasgow, Newcastle, Port Harcourt and Kano to `LOCATIONS`
- [ ] **Battery autonomy days:** add `--autonomy-days` so off-grid users can size for cloudy spells
- [ ] **`loads` command:** print a table of each appliance's daily energy and share of the total
- [ ] **Markdown report:** add `--markdown` output for pasting into documents

## Medium
- [ ] **Monthly solar table:** store 12 monthly sun-hour values per location and print output month by month
- [ ] **Turbine power curves from CSV:** read real manufacturer power curves instead of the simple cubic model
- [ ] **Weibull distribution:** let users set the wind shape factor (Rayleigh is the special case k = 2)
- [ ] **Costs and payback:** add equipment prices, electricity tariff and Smart Export Guarantee rate to estimate payback years
- [ ] **Panel orientation:** adjust output for east/west-facing roofs and different tilts

## Bigger ideas
- [ ] **Generator backup sizing** for the winter shortfall
- [ ] **Hourly simulation** of a typical day with battery state of charge
- [ ] **Web version** of the calculator
- [ ] **Publish to PyPI** so people can `pip install solarwind`
