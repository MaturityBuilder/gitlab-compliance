#!/usr/bin/env bash
# sessionStart: open a GitHub tracking issue for this agent session.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HOOK_DIR/../.." && pwd)"
source "$ROOT/.cursor/hooks/lib/github-issues.sh"

input="$(cat)"
issue_file="$(agent_issue_file "$ROOT")"

if [[ -f "$issue_file" ]]; then
  num="$(read_agent_issue_number "$ROOT" || true)"
  if [[ -n "${num:-}" ]]; then
    python3 -c 'import json,sys; print(json.dumps({"continue": True, "env": {"CURSOR_AGENT_ISSUE_NUMBER": sys.argv[1]}}))' "$num"
    exit 0
  fi
fi

if ! ensure_gh_auth; then
  echo '{"continue": true}' >&2
  exit 0
fi

repo_root="$(detect_repo_root "$ROOT")"
repo="$(cd "$repo_root" && gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
[[ -n "$repo" ]] || exit 0

eval "$(echo "$input" | python3 - <<'PY'
import json, os, shlex, sys
raw = sys.stdin.read()
try:
    data = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    data = {}
title = "Agent: Cloud Agent session"
for key in ("prompt", "user_message", "initial_prompt", "message"):
    val = data.get(key)
    if isinstance(val, str) and val.strip():
        title = "Agent: " + val.strip().splitlines()[0][:120]
        break
lines = [
    "Tracking issue for a Cursor Cloud Agent session.",
    "",
    "Commits and pull requests for this work should reference this issue number.",
]
for key in ("conversation_id", "bc_id", "agent_id"):
    if data.get(key):
        lines.append(f"- **{key}**: `{data[key]}`")
if os.environ.get("CURSOR_CONVERSATION_ID"):
    lines.append(f"- **conversation**: `{os.environ['CURSOR_CONVERSATION_ID']}`")
body = "\n".join(lines)
print(f"title={shlex.quote(title)}")
print(f"body={shlex.quote(body)}")
PY
)"

json_out="$(gh issue create -R "$repo" --title "$title" --body "$body" --label "cloud-agent" --json number,url 2>/dev/null || \
  gh issue create -R "$repo" --title "$title" --body "$body" --json number,url 2>/dev/null || true)"

[[ -n "$json_out" ]] || exit 0

number="$(printf '%s' "$json_out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["number"])')"
url="$(printf '%s' "$json_out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["url"])')"
write_agent_issue "$ROOT" "$number" "$url" "$title"

python3 -c 'import json,sys; n,u=sys.argv[1],sys.argv[2]; print(json.dumps({"continue": True, "env": {"CURSOR_AGENT_ISSUE_NUMBER": n, "CURSOR_AGENT_ISSUE_URL": u}, "user_message": f"Opened GitHub tracking issue #{n}. Reference #{n} or Fixes #{n} in commits and PRs."}))' "$number" "$url"
