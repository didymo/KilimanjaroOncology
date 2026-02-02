#!/usr/bin/env bash
set -uo pipefail

# Always run all checks; accumulate failures.
rc=0

echo "== quality gate (conservative) =="
echo "Working directory: $(pwd)"

# --- Ruff (lint only; NO auto-fix) ---
echo "--- ruff (check only) ---"
if ! uv run ruff check .; then
  rc=1
fi

# --- Tests (if installed) ---
echo "--- tests ---"
if uv run python -c "import pytest" >/dev/null 2>&1; then
  # Prefer coverage if pytest-cov is installed
  if uv run python -c "import pytest_cov" >/dev/null 2>&1; then
    if ! uv run pytest --cov --cov-report=term-missing; then
      rc=1
    fi
  else
    if ! uv run pytest; then
      rc=1
    fi
  fi
else
  echo "pytest not installed; skipping tests."
fi

# --- Types (if installed) ---
echo "--- mypy ---"
if uv run python -c "import mypy" >/dev/null 2>&1; then
  if ! uv run mypy .; then
    rc=1
  fi
else
  echo "mypy not installed; skipping type checks."
fi

# --- Dependency vulnerabilities ---
echo "--- pip-audit ---"
if ! uv run pip-audit; then
  rc=1
fi

# --- Static security analysis (if installed) ---
echo "--- bandit ---"
if uv run python -c "import bandit" >/dev/null 2>&1; then
  # -q reduces noise; config explicitly from pyproject.toml
  if ! uv run bandit -q -c pyproject.toml -r .; then
    rc=1
  fi
else
  echo "bandit not installed; skipping SAST."
fi

# --- Optional deep security (Semgrep CE) ---
# For medical/PII work, run explicitly when needed:
#   DEEP=1 ./tools/quality-gate.sh
if [[ "${DEEP:-0}" == "1" ]]; then
  echo "--- semgrep (deep security) ---"
  if [[ -x "./tools/security-deep.sh" ]]; then
    if ! ./tools/security-deep.sh ERROR; then
      rc=1
    fi
  else
    echo "tools/security-deep.sh not found or not executable; skipping Semgrep."
    echo "Hint: run: python3 /path/to/py_guardrails.py gate"
  fi
fi


if [[ "$rc" -eq 0 ]]; then
  echo "OK"
else
  echo "FAILED (one or more checks)."
fi
exit "$rc"
