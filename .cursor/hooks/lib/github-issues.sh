#!/usr/bin/env bash
# Shared helpers for GitHub Issues hooks (Cloud Agent PAT in GITHUB_ISSUES).
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

ensure_gh_auth() {
  local pat
  pat="$(pick_pat)" || return 1
  printf '%s\n' "$pat" | gh auth login --with-token >/dev/null 2>&1
  export GH_TOKEN="$pat"
  export GITHUB_TOKEN="$pat"
}

agent_issue_file() {
  local root="${1:-.}"
  printf '%s/.cursor/agent-issue.json' "$root"
}

read_agent_issue_number() {
  local root="${1:-.}" file num
  file="$(agent_issue_file "$root")"
  [[ -f "$file" ]] || return 1
  num="$(python3 - "$file" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
print(data.get("number", ""))
PY
)" || return 1
  [[ -n "$num" ]] || return 1
  printf '%s' "$num"
}

write_agent_issue() {
  local root="${1:-.}" number url title
  number="$2"
  url="$3"
  title="${4:-}"
  mkdir -p "$root/.cursor"
  python3 - "$root" "$number" "$url" "$title" <<'PY'
import json, sys
from pathlib import Path
root, number, url, title = sys.argv[1:5]
path = Path(root) / ".cursor" / "agent-issue.json"
path.write_text(
    json.dumps(
        {"number": int(number), "url": url, "title": title},
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
}

detect_repo_root() {
  local root="${1:-.}"
  (cd "$root" && git rev-parse --show-toplevel 2>/dev/null) || printf '%s' "$root"
}

reference_contains_issue() {
  local text="$1" num="$2"
  python3 - "$text" "$num" <<'PY'
import re, sys
text, num = sys.argv[1], sys.argv[2]
patterns = [
    rf"#\s*{re.escape(num)}\b",
    rf"fixes\s+#\s*{re.escape(num)}\b",
    rf"closes\s+#\s*{re.escape(num)}\b",
    rf"resolves\s+#\s*{re.escape(num)}\b",
    rf"\(\s*#{re.escape(num)}\s*\)",
]
print("1" if any(re.search(p, text, re.I) for p in patterns) else "0")
PY
}
