# AGENTS.md

## Command execution
- When you execute a shell command, launch the shell with `login:false`.

## Project overview
- Python/Tkinter desktop app for oncology data collection.
- Code lives under `src/kilimanjaro_oncology`.
- Tests in `tests/`.

## Environment
- Python 3.12 per `pyproject.toml`.
- Uses Poetry for dependency management, but editable `pip` install also works.

## Common commands
- Run app: `python -m kilimanjaro_oncology.main`
- Run tests: `python -m pytest`

## Linting and formatting (run regularly, but must not block a commit)
- Black: `black .`
- isort: `isort .`
- Flake8: `flake8`
- Mypy: `mypy src tests`
- Pre-commit: `pre-commit run --all-files`

## Tox environments
- Full check suite: `tox`
- Pre-commit: `tox -e pre-commit`
- Type-check: `tox -e type-check`
- Safety scan: `tox -e safety`

## Notes
- There appears to be a bug; capture a minimal reproduction and note expected vs actual behavior in any fix PR.
- Lint/test failures should be reported, but do not block committing changes unless explicitly requested.
