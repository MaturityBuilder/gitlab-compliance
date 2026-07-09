#!/usr/bin/env bash
# Source or run before gh issue/project commands in Cloud Agents:
#   source scripts/gh-issues-auth.sh
set -euo pipefail

if [[ -z "${GITHUB_ISSUES:-}" ]]; then
  echo "GITHUB_ISSUES secret is not set in this VM." >&2
  echo "Add it under Cloud Agents → Environment → Secrets, then Update Existing Env." >&2
  return 1 2>/dev/null || exit 1
fi

printf '%s\n' "$GITHUB_ISSUES" | gh auth login --with-token
export GH_TOKEN="$GITHUB_ISSUES"
export GITHUB_TOKEN="$GITHUB_ISSUES"
