#!/usr/bin/env bash
# beforeShellExecution: require tracking issue reference in git commit commands.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/.cursor/hooks/lib/github-issues.sh"

input="$(cat)"
command="$(printf '%s' "$input" | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get("command") or data.get("cmd") or "")')"

allow() {
  echo '{"permission": "allow"}'
  exit 0
}

deny() {
  local msg="$1"
  python3 - "$msg" <<'PY'
import json, sys
msg = sys.argv[1]
print(json.dumps({
    "permission": "deny",
    "user_message": msg,
    "agent_message": msg,
}))
PY
  exit 0
}

[[ "$command" =~ git[[:space:]]+commit ]] || allow

num="$(read_agent_issue_number "$ROOT" 2>/dev/null || true)"
[[ -n "${num:-}" ]] || allow

# Extract -m / --message values from the shell command string.
messages="$(printf '%s' "$command" | python3 <<'PY'
import re, sys
cmd = sys.stdin.read()
parts = []
for m in re.finditer(r'-m\s+(["\'])(.*?)\1', cmd):
    parts.append(m.group(2))
for m in re.finditer(r'--message(?:=|\s+)(["\'])(.*?)\1', cmd):
    parts.append(m.group(2))
print("\n".join(parts))
PY
)"

check_text="$command"
[[ -n "$messages" ]] && check_text="$messages"

if [[ "$(reference_contains_issue "$check_text" "$num")" == "1" ]]; then
  allow
fi

deny "Commit must reference tracking issue #${num} (e.g. Fixes #${num} or include #${num} in the message)."
