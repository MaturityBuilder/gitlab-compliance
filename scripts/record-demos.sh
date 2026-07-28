#!/usr/bin/env bash
# Record documentation demo GIFs with VHS.
#
# Usage:
#   bash scripts/record-demos.sh offline   # default; no GitLab token
#   bash scripts/record-demos.sh live      # requires GITLAB_TOKEN + DEMO_PROJECT
#   bash scripts/record-demos.sh all
#   bash scripts/record-demos.sh screenshots  # HTML report/doc PNGs only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

DEMOS_DIR="${ROOT}/docs/demos"
TAPES_DIR="${DEMOS_DIR}/tapes"
GIFS_DIR="${DEMOS_DIR}/gifs"
SHOTS_DIR="${DEMOS_DIR}/screenshots"
FIXTURES="${DEMOS_DIR}/fixtures"
OUT_TMP="${DEMOS_DIR}/.tmp"

OFFLINE_TAPES=(
  check-console.tape
  check-markdown.tape
  check-html.tape
  check-mr-comment-body.tape
  check-create-mr-offline.tape
  shell-check-console.tape
  shell-check-markdown.tape
  generate-markdown.tape
  generate-html.tape
  get-attributes.tape
  policies-doc.tape
  document-gitstrings.tape
)

LIVE_TAPES=(
  check-mr-comment.tape
  check-create-mr.tape
  release-notes.tape
  policies-push-pull.tape
)

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: required command not found: $1" >&2
    echo "See docs/demos/README.md for install steps." >&2
    exit 1
  fi
}

ensure_poetry_cli() {
  if ! poetry run gitlab-compliance --help >/dev/null 2>&1; then
    echo "error: poetry run gitlab-compliance failed; run poetry install first" >&2
    exit 1
  fi
}

# Prefer poetry-run wrapper so tapes can call a stable binary name.
install_cli_shim() {
  mkdir -p "${OUT_TMP}/bin"
  cat >"${OUT_TMP}/bin/gitlab-compliance" <<'EOF'
#!/usr/bin/env bash
exec poetry run gitlab-compliance "$@"
EOF
  chmod +x "${OUT_TMP}/bin/gitlab-compliance"
  export PATH="${OUT_TMP}/bin:${PATH}"
}

record_tape() {
  local tape="$1"
  local path="${TAPES_DIR}/${tape}"
  if [[ ! -f "${path}" ]]; then
    echo "error: missing tape ${path}" >&2
    exit 1
  fi
  echo "==> recording ${tape}"
  (
    cd "${ROOT}"
    vhs "${path}"
  )
}

record_list() {
  local tape
  for tape in "$@"; do
    record_tape "${tape}"
  done
}

png_to_gif() {
  # Hold a rendered screenshot as a short looping GIF for docs embeds.
  local src="$1"
  local dest="$2"
  require_cmd ffmpeg
  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -t 8 -i "${src}" \
    -vf "fps=8,scale=1280:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
    "${dest}"
  echo "Wrote ${dest}"
}

capture_html_screenshots() {
  require_cmd google-chrome
  require_cmd ffmpeg
  mkdir -p "${SHOTS_DIR}" "${GIFS_DIR}" "${OUT_TMP}"
  install_cli_shim
  ensure_poetry_cli

  local report_html="${OUT_TMP}/compliance-report.html"
  local docs_html="${OUT_TMP}/pipeline-docs.html"
  local mr_comment_md="${OUT_TMP}/mr-comment.md"

  gitlab-compliance check \
    -f "${FIXTURES}/policies" \
    -p "${FIXTURES}/.gitlab-ci.yml" \
    --format html \
    -o "${report_html}" || true

  gitlab-compliance check \
    -f "${FIXTURES}/policies" \
    -p "${FIXTURES}/.gitlab-ci.yml" \
    --format mr-comment \
    -o "${mr_comment_md}" || true

  gitlab-compliance generate \
    -i "${FIXTURES}/.gitlab-ci.yml" \
    --format html \
    -o "${docs_html}"

  # file:// URLs; window-size keeps tables readable
  google-chrome --headless --disable-gpu --no-sandbox \
    --window-size=1280,900 \
    --screenshot="${SHOTS_DIR}/check-html-report.png" \
    "file://${report_html}" >/dev/null 2>&1

  google-chrome --headless --disable-gpu --no-sandbox \
    --window-size=1280,900 \
    --screenshot="${SHOTS_DIR}/generate-html-docs.png" \
    "file://${docs_html}" >/dev/null 2>&1

  # HTML demo GIFs must show the *rendered* page, not source dumps from VHS.
  png_to_gif "${SHOTS_DIR}/check-html-report.png" "${GIFS_DIR}/check-html.gif"
  png_to_gif "${SHOTS_DIR}/generate-html-docs.png" "${GIFS_DIR}/generate-html.gif"

  poetry run python - "${mr_comment_md}" "${OUT_TMP}" <<'PY'
import html
import sys
from pathlib import Path

body = Path(sys.argv[1]).read_text(encoding="utf-8")
out = Path(sys.argv[2])
escaped = html.escape(body)
(out / "mr-comment-ui.html").write_text(
    f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MR comment preview</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  margin: 0; background: #fafafa; color: #1f1f1f; }}
.frame {{ max-width: 920px; margin: 24px auto; background: #fff;
  border: 1px solid #d0d7de; border-radius: 8px; }}
.header {{ padding: 12px 16px; border-bottom: 1px solid #d0d7de; font-weight: 600; }}
.meta {{ color: #656d76; font-weight: 400; font-size: 14px; }}
.body {{ padding: 16px; white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px; line-height: 1.45; }}
.badge {{ display: inline-block; background: #ddf4ff; color: #0969da;
  border-radius: 2em; padding: 2px 8px; font-size: 12px; }}
</style></head><body>
<div class="frame">
  <div class="header">gitlab-compliance <span class="meta">commented on merge request !42</span>
    <div><span class="badge">from --post-mr-comment</span></div>
  </div>
  <div class="body">{escaped}</div>
</div>
</body></html>""",
    encoding="utf-8",
)
(out / "create-mr-ui.html").write_text(
    """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MR create preview</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  margin: 0; background: #fafafa; color: #1f1f1f; }
.frame { max-width: 920px; margin: 24px auto; background: #fff;
  border: 1px solid #d0d7de; border-radius: 8px; padding: 20px; }
h1 { font-size: 20px; margin: 0 0 8px; }
.branch { color: #656d76; font-size: 14px; margin-bottom: 16px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 20px; }
th, td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; font-size: 13px; }
th { background: #f6f8fa; }
ol { font-size: 14px; line-height: 1.5; }
.badge { display: inline-block; background: #dafbe1; color: #1a7f37;
  border-radius: 2em; padding: 2px 8px; font-size: 12px; }
</style></head><body>
<div class="frame">
  <div class="badge">opened by --create-mr</div>
  <h1>gitlab-compliance supply-chain fixes</h1>
  <div class="branch">gitlab-compliance/supply-chain-fix → main</div>
  <table>
    <tr><th>Change</th><th>Count</th></tr>
    <tr><td>Image pins (sha256)</td><td>1</td></tr>
    <tr><td>Include ref bumps</td><td>0</td></tr>
  </table>
  <ol>
    <li>Pinned <code>build</code> image <code>alpine:3.19</code> to digest</li>
  </ol>
</div>
</body></html>""",
    encoding="utf-8",
)
print("wrote mock MR HTML")
PY

  google-chrome --headless --disable-gpu --no-sandbox \
    --window-size=1000,900 \
    --screenshot="${SHOTS_DIR}/check-post-mr-comment-ui.png" \
    "file://${OUT_TMP}/mr-comment-ui.html" >/dev/null 2>&1

  google-chrome --headless --disable-gpu --no-sandbox \
    --window-size=1000,700 \
    --screenshot="${SHOTS_DIR}/check-create-mr-ui.png" \
    "file://${OUT_TMP}/create-mr-ui.html" >/dev/null 2>&1

  echo "Wrote ${SHOTS_DIR}/check-html-report.png"
  echo "Wrote ${SHOTS_DIR}/generate-html-docs.png"
  echo "Wrote ${SHOTS_DIR}/check-post-mr-comment-ui.png"
  echo "Wrote ${SHOTS_DIR}/check-create-mr-ui.png"
  echo "Wrote ${GIFS_DIR}/check-html.gif (rendered)"
  echo "Wrote ${GIFS_DIR}/generate-html.gif (rendered)"
}

require_live_env() {
  if [[ -z "${GITLAB_TOKEN:-}" ]]; then
    echo "error: GITLAB_TOKEN is required for live demos" >&2
    exit 1
  fi
  if [[ -z "${DEMO_PROJECT:-}" ]]; then
    echo "error: DEMO_PROJECT is required for live demos (e.g. group/project)" >&2
    exit 1
  fi
  export DEMO_GITLAB_URL="${DEMO_GITLAB_URL:-https://gitlab.com}"
}

mode="${1:-offline}"

require_cmd vhs
require_cmd ffmpeg
require_cmd ttyd
ensure_poetry_cli
install_cli_shim
mkdir -p "${GIFS_DIR}" "${SHOTS_DIR}" "${OUT_TMP}"

case "${mode}" in
  offline)
    record_list "${OFFLINE_TAPES[@]}"
    capture_html_screenshots
    ;;
  live)
    require_live_env
    record_list "${LIVE_TAPES[@]}"
    ;;
  screenshots)
    capture_html_screenshots
    ;;
  all)
    record_list "${OFFLINE_TAPES[@]}"
    capture_html_screenshots
    require_live_env
    record_list "${LIVE_TAPES[@]}"
    ;;
  *)
    echo "usage: $0 [offline|live|screenshots|all]" >&2
    exit 2
    ;;
esac

echo "Done (${mode}). GIFs in ${GIFS_DIR}"
