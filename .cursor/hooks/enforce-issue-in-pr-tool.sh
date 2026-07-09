#!/usr/bin/env bash
# preToolUse: ensure ManagePullRequest title/body references the session tracking issue.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HOOK_DIR/../.." && pwd)"
source "$ROOT/.cursor/hooks/lib/github-issues.sh"

input="$(cat)"

INPUT_JSON="$input" python3 - "$ROOT" <<'PY'
import json
import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
raw = os.environ.get("INPUT_JSON", "")
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

tool_name = data.get("tool_name") or data.get("name") or ""
if "ManagePullRequest" not in tool_name:
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

issue_path = root / ".cursor" / "agent-issue.json"
if not issue_path.is_file():
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

try:
    issue = json.loads(issue_path.read_text(encoding="utf-8"))
    num = str(issue["number"])
except (KeyError, json.JSONDecodeError, OSError):
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

args = data.get("tool_input") or data.get("arguments") or data.get("input") or {}
if isinstance(args, str):
    try:
        args = json.loads(args)
    except json.JSONDecodeError:
        args = {}

action = (args.get("action") or "").lower()
if action not in ("create_pr", "update_pr"):
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

title = args.get("title") or ""
body = args.get("body") or ""
combined = f"{title}\n{body}"
patterns = [
    rf"#\s*{re.escape(num)}\b",
    rf"fixes\s+#\s*{re.escape(num)}\b",
    rf"closes\s+#\s*{re.escape(num)}\b",
    rf"resolves\s+#\s*{re.escape(num)}\b",
]
if any(re.search(p, combined, re.I) for p in patterns):
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

suffix = f"\n\nResolves #{num}"
if body.strip():
    args["body"] = body.rstrip() + suffix
else:
    args["body"] = f"Resolves #{num}".strip()

print(
    json.dumps(
        {
            "permission": "allow",
            "updated_input": args,
            "agent_message": f"Appended Resolves #{num} to the pull request body.",
        }
    )
)
PY
