#!/usr/bin/env bash
# Source before gh issue/project commands:
#   source scripts/gh-issues-auth.sh
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

if ! pat="$(pick_pat)"; then
  echo "No PAT in GITHUB_ISSUES, GITHUB_TOKEN, or GH_TOKEN (non-ghs_)." >&2
  return 1 2>/dev/null || exit 1
fi

printf '%s\n' "$pat" | gh auth login --with-token
export GH_TOKEN="$pat"
export GITHUB_TOKEN="$pat"
