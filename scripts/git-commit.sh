#!/usr/bin/env bash
# Run full pre-commit checks, then git commit (pass-through args).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"${ROOT}/scripts/pre-commit-check.sh"
exec git commit "$@"
