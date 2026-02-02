#!/usr/bin/env bash
set -euo pipefail

echo "== auto-fix (explicit) =="
echo "Working directory: $(pwd)"
echo "Note: this may change files. Review diffs before committing."

# Apply Ruff auto-fixes where possible
uv run ruff check . --fix

# Optional: apply Ruff formatter (safe + consistent)
uv run ruff format .

# Format with Black if installed (optional). Some teams prefer Black over Ruff format.
if uv run python -c "import black" >/dev/null 2>&1; then
  uv run black .
else
  echo "black not installed; skipping Black formatting."
  echo "Hint: install Black via bootstrap --use-black (or: uv add --dev black)."
fi

echo "OK"
