
# AGENTS.md

## Command execution
- When you execute a shell command, launch the shell with `login:false`.

## Project overview
- Python/Tkinter desktop app for oncology data collection.
- Code lives under `src/kilimanjaro_oncology`.
- Tests in `tests/`.

## Environment
- Python 3.12 per `pyproject.toml`.

## Common commands
- Run app: `python -m kilimanjaro_oncology.main`
- Run tests: `python -m pytest`

## Notes
- There appears to be a bug; capture a minimal reproduction and note expected vs actual behavior in any fix PR.

## TDD expectations
- Test suite first: implement or extend tests before any production code changes for a feature or bug fix.
- Code only after failing tests: ensure new/updated tests fail for the right reason, then implement the code to make them pass.
- Keep tests focused: run a small, relevant subset during development, then run the full suite before finalizing.
- For bug fixes: include a minimal reproduction test in `tests/` and note expected vs actual behavior.

---

## AI Agent Quality & Safety Requirements (Medical / PII Context)

This repository contains **medical data and potentially identifiable information (PII)**.

The following requirements define the **mandatory Definition of Done for any AI-generated or AI-modified code**.

These rules override informal guidance when safety, correctness, or security is involved.

---

### 1. Mandatory Conservative Quality Gate

Before considering work complete, the agent **must run and report the results of**:

```bash
./tools/quality-gate.sh

