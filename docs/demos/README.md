# Documentation demos (VHS)

Reproducible terminal GIFs for Usage / CLI pages, recorded with
[VHS](https://github.com/charmbracelet/vhs).

## Layout

| Path | Purpose |
| ---- | ------- |
| `fixtures/` | Tiny pipeline YAML + policies for offline tapes |
| `tapes/` | VHS `.tape` sources |
| `gifs/` | Committed GIF outputs (terminal VHS + rendered HTML) |
| `screenshots/` | HTML report/doc PNGs and GitLab MR UI stills |

HTML format demos (`check-html.gif`, `generate-html.gif`) are **browser
screenshots** converted to GIF (not VHS source dumps). Matching CLI tapes write
`*-html-cli.gif` only.

## Prerequisites

- Poetry env with `gitlab-compliance` installed (`poetry install`)
- [VHS](https://github.com/charmbracelet/vhs/releases) on `PATH`
- `ttyd` and `ffmpeg` on `PATH`
- A Chromium/Chrome binary named `google-chrome` or `chromium` (Playwright’s
  Chromium works via symlink)

Example local install (Linux x86_64):

```bash
# vhs + ttyd into ~/.local/bin
curl -sL https://github.com/charmbracelet/vhs/releases/download/v0.11.0/vhs_0.11.0_Linux_x86_64.tar.gz \
  | tar -xz -C /tmp
install -m 755 /tmp/vhs_0.11.0_Linux_x86_64/vhs ~/.local/bin/vhs
curl -sL https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 \
  -o ~/.local/bin/ttyd && chmod +x ~/.local/bin/ttyd
# ffmpeg: system package or a static build on PATH
export PATH="$HOME/.local/bin:$PATH"
```

## Record

From the repository root:

```bash
# Offline (no GitLab token) — default for contributors / CI
bash scripts/record-demos.sh offline

# HTML PNGs only
bash scripts/record-demos.sh screenshots

# Live GitLab / OCI demos
export GITLAB_TOKEN=…          # PAT or project token (api + write for create-mr)
export DEMO_PROJECT=group/project
export DEMO_GITLAB_URL=https://gitlab.com   # optional
export DEMO_MR_IID=123                      # for post-mr-comment
export DEMO_OCI_REF=registry.example.com/org/demo-policies:demo
bash scripts/record-demos.sh live
```

`offline` regenerates committed GIFs under `gifs/` and HTML screenshots under
`screenshots/`. Live tapes also write GIFs; capture GitLab MR UI PNGs manually
into `screenshots/` (scrub tokens) after a successful run:

- `screenshots/check-create-mr-ui.png` — MR description after `--create-mr`
- `screenshots/check-post-mr-comment-ui.png` — note posted by `--post-mr-comment`

## Embedding

| GIF | Doc page |
| --- | -------- |
| `check-console.gif` | [check](../usage/reference/check.md), [Usage](../usage/index.md), [Overview](../index.md) |
| `check-markdown.gif` | [check](../usage/reference/check.md), [Usage](../usage/index.md) |
| `check-html-cli.gif` / `check-html.gif` | [check](../usage/reference/check.md), [Usage](../usage/index.md) |
| `check-mr-comment.gif` | [check](../usage/reference/check.md) (`--post-mr-comment`), [Usage](../usage/index.md) |
| `check-create-mr.gif` | [check](../usage/reference/check.md) (`--create-mr`), [Auto-fix](../usage/fix-policies.md), [Usage](../usage/index.md) |
| `generate-markdown.gif` | [generate](../usage/reference/generate.md), [Usage](../usage/index.md) |
| `generate-html-cli.gif` / `generate-html.gif` | [generate](../usage/reference/generate.md), [Usage](../usage/index.md) |
| `get-attributes.gif` | [get-attributes](../usage/reference/get-attributes.md), [Usage](../usage/index.md) |
| `policies-doc.gif` | [policies doc](../usage/reference/policies-doc.md), [Usage](../usage/index.md) |
| `document-gitstrings.gif` | [document gitstrings](../usage/reference/document-gitstrings.md), [Gitstrings](../usage/gitstrings.md), [Usage](../usage/index.md) |

Tapes use `TypingSpeed 40ms` and `PlaybackSpeed 0.5`; rendered HTML GIFs hold
~8s. Keep frames free of secrets.

## CI

GitHub Actions job `demos-offline` installs VHS and ttyd with
`scripts/install-ci-demo-tools.sh` (pinned VHS release tarball SHA256; ttyd built
from a pinned source commit), validates offline tapes, and fails if committed GIF
outputs are missing (regenerate with `bash scripts/record-demos.sh offline` when
tapes change).
