#!/usr/bin/env bash
set -euo pipefail

echo "== deep security (semgrep CE) =="
echo "Working directory: $(pwd)"

# Usage:
#   ./tools/security-deep.sh              -> ERROR severity (low noise)
#   ./tools/security-deep.sh WARNING      -> broader scan
#
# For medical/PII work, you often want to scan *everything*, not just git-tracked files.
# This script defaults to scanning all files under the repo (respects .semgrepignore if present).

SEVERITY="${1:-ERROR}"

case "$SEVERITY" in
  ERROR|WARNING) ;;
  *)
    echo "Invalid severity: $SEVERITY (use ERROR or WARNING)"
    exit 2
    ;;
esac

# Ensure Semgrep is available as a uv tool.
if ! uv tool run semgrep --version >/dev/null 2>&1; then
  echo "semgrep is not available as a uv tool."
  echo "Install it with: uv tool install semgrep"
  echo "If that fails under Python 3.12, try: uv tool install --python 3.11 semgrep"
  exit 2
fi

echo "Severity: $SEVERITY"
echo "Rulepacks: p/security-audit + p/python"
echo "Mode: scan all files (not just git-tracked)"

uv tool run semgrep \
  --config=p/security-audit \
  --config=p/python \
  --severity="$SEVERITY" \
  --no-git-ignore \
  .
