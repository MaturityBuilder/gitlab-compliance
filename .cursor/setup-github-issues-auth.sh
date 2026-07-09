#!/usr/bin/env bash
# Authenticate GitHub CLI for Issues/Projects using the GITHUB_ISSUES runtime secret.
# Cursor injects GITHUB_ISSUES from the Cloud Agent environment Secrets panel.
set -euo pipefail

wait_for_secret() {
  local i
  for i in $(seq 1 60); do
    if [[ -n "${GITHUB_ISSUES:-}" ]]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

if ! wait_for_secret; then
  echo "GITHUB_ISSUES is not set; gh will keep using the Cursor App token (no issues scope)." >&2
  exit 0
fi

printf '%s\n' "$GITHUB_ISSUES" | gh auth login --with-token
export GH_TOKEN="$GITHUB_ISSUES"

login="$(gh api user -q .login 2>/dev/null || true)"
if [[ -n "$login" && "$login" != "cursor[bot]" ]]; then
  echo "gh authenticated for Issues as: $login"
else
  echo "gh auth login completed but user is still cursor[bot] or unknown; check PAT scopes." >&2
fi
