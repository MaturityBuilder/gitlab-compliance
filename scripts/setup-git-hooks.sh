#!/usr/bin/env bash
# Point git at repo hooks and install pre-commit hook environments.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

chmod +x .githooks/pre-commit
git config core.hooksPath .githooks

if command -v poetry >/dev/null 2>&1; then
  poetry install --no-interaction
  poetry run pre-commit install-hooks
  echo "Installed pre-commit hook environments and set core.hooksPath=.githooks"
else
  echo "Set core.hooksPath=.githooks (install Poetry and re-run to fetch hook envs)." >&2
fi
