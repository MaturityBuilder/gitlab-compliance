#!/usr/bin/env bash
# Authenticate GitHub CLI for Issues/Projects using dashboard runtime secrets.
set -euo pipefail

pick_pat() {
  local v
  for v in "${GITHUB_ISSUES:-}" "${GITHUB_TOKEN:-}" "${GH_TOKEN:-}"; do
    [[ -z "$v" ]] && continue
    [[ "$v" == ghs_* ]] && continue
    printf '%s' "$v"
    return 0
  done
  return 1
}

wait_for_pat() {
  local i pat
  for i in $(seq 1 30); do
    if pat="$(pick_pat)"; then
      printf '%s' "$pat"
      return 0
    fi
    sleep 1
  done
  return 1
}

if ! pat="$(wait_for_pat)"; then
  echo "No Issues PAT in GITHUB_ISSUES / GITHUB_TOKEN / GH_TOKEN; gh keeps cursor[bot]." >&2
  exit 0
fi

printf '%s\n' "$pat" | gh auth login --with-token
export GH_TOKEN="$pat"
export GITHUB_TOKEN="$pat"

login="$(gh api user -q .login 2>/dev/null || true)"
if [[ -n "$login" && "$login" != "cursor[bot]" ]]; then
  echo "gh authenticated for Issues as: $login"
fi
