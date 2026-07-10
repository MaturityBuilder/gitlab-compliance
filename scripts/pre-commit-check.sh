#!/usr/bin/env bash
# Run all pre-commit hooks (same as CI: poetry run pre-commit run --all-files).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${HOME}/.pyenv/shims:${PATH}"

if ! command -v poetry >/dev/null 2>&1; then
  echo "error: Poetry is required. See docs/contributing.md" >&2
  exit 1
fi

poetry run pre-commit run --all-files
