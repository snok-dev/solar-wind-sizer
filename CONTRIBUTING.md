# Contributing

Thanks for helping! Here's how to work on the project.

## Set up

```bash
git clone https://github.com/snok-dev/solar-wind-sizer.git
cd solar-wind-sizer
python3 -m venv .venv
source .venv/bin/activate        # Windows (WSL2) too
python3 -m pip install -e ".[dev]"
python3 -m pytest
```

New to git? Work through [docs/GIT_GUIDE.md](docs/GIT_GUIDE.md) first.

## Workflow

1. **Pick or open an issue** describing the change.
2. **Create a branch** from `main`: `git switch -c add-glasgow-location`
3. **Make small commits** with clear messages: "Add Glasgow sun hours", not "update".
4. **Add or update tests** in `tests/` and make sure `python3 -m pytest` passes.
5. **Push and open a pull request** that links the issue ("Closes #12").
6. GitHub runs the tests automatically. Once they're green, merge.

## Style

- Keep functions small, with a docstring saying what they return and in which units.
- Units go in names where it helps: `daily_kwh`, `rated_watts`, `hub_height`.
- No outside libraries in the main package. It should stay easy to install.
