"""Danger checks for pull requests."""

import re

from danger import danger, message, warn

PR_TITLE = danger.github.pr.title if danger.github.pr else ""

CONVENTIONAL_COMMIT = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\(.+\))?!?:\s+.+",
    re.IGNORECASE,
)

MAX_CHANGED_LINES = 500

changed_files = [f for f in danger.git.modified_files + danger.git.created_files]
deleted_files = danger.git.deleted_files
all_touched = changed_files + deleted_files

additions = danger.github.pr.additions if danger.github.pr else 0
deletions = danger.github.pr.deletions if danger.github.pr else 0
total_changed = additions + deletions

if total_changed > MAX_CHANGED_LINES:
    warn(
        f"This PR changes {total_changed} lines (limit {MAX_CHANGED_LINES}). "
        "Consider splitting into smaller PRs for easier review."
    )

src_changed = any(f.startswith("src/") for f in all_touched)
tests_changed = any(f.startswith("tests/") for f in all_touched)
docs_changed = any(f.startswith("docs/") for f in all_touched)
ci_changed = any(
    f.endswith((".yml", ".yaml"))
    and (
        f.startswith(".github/workflows/")
        or f == ".gitlab-ci.yml"
        or f.startswith("examples/")
    )
    for f in all_touched
)

if src_changed and not tests_changed:
    warn(
        "Source files changed without test updates. "
        "Add or update tests under `tests/` when behavior changes."
    )

if src_changed and not docs_changed:
    warn(
        "Source files changed without documentation updates. "
        "Update `docs/` for user-facing CLI or compliance changes."
    )

if ci_changed:
    message(
        "CI configuration changed. See "
        "[`.github/workflows/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/.github/workflows) "
        "and run `poetry run pre-commit run --all-files` locally."
    )

if PR_TITLE and not CONVENTIONAL_COMMIT.match(PR_TITLE):
    message(
        "Consider a [Conventional Commits](https://www.conventionalcommits.org/) "
        f"PR title (e.g. `feat: ...`, `fix: ...`). Current title: `{PR_TITLE}`"
    )

workflow_only = all(
    f.startswith(".github/workflows/") or f == "dangerfile.py" for f in all_touched
)
if workflow_only and not PR_TITLE.lower().startswith("ci"):
    message("Workflow-only change detected — `ci:` prefix in the PR title is recommended.")
