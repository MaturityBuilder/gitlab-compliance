#!/usr/bin/env python3
"""Explicit CI checks (used when pytest logs are hard to retrieve)."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _summary(line: str) -> None:
    print(line)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def _check(name: str, fn) -> bool:
    try:
        fn()
        _summary(f"- [x] {name}")
        return True
    except Exception as exc:
        _summary(f"- [ ] **{name}**: `{exc}`")
        traceback.print_exc()
        return False


def main() -> int:
    from src.modules.constants import GLDOCS_CLOSING_MARKER, GLDOCS_OPENING_MARKER
    from src.modules.pipeline import generate_documentation_body
    from src.modules.render import DocTable, render_table
    from src.modules.reset_docs import merge_markdown_output
    from src.properties.sections.variables import build_variables_section
    from src.properties.sections.workflows import build_workflows_section

    repo_ci = ROOT / ".gitlab-ci.yml"
    sample_ci = ROOT / "sample-files" / ".gitlab-ci.yml"

    ok = True
    ok &= _check(
        "variables section",
        lambda: (
            "App name"
            in build_variables_section(
                {
                    "variables": {
                        "RUNNER": "docker",
                        "APPLICATION": {
                            "value": "gitlab-docs",
                            "description": "App name",
                        },
                    }
                }
            )
        ),
    )
    ok &= _check(
        "workflow rules dict",
        lambda: "merge_request_event"
        in build_workflows_section(
            {
                "workflow": {
                    "rules": [
                        {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'},
                        {"when": "never"},
                    ]
                }
            }
        ),
    )
    ok &= _check(
        "repo pipeline markdown",
        lambda: "MEGALINTER" in generate_documentation_body(repo_ci),
    )
    ok &= _check(
        "sample pipeline markdown",
        lambda: bool(generate_documentation_body(sample_ci).strip()),
    )
    ok &= _check(
        "workflow on repo ci",
        lambda: "Workflow"
        in generate_documentation_body(repo_ci, document_workflows=True),
    )
    ok &= _check(
        "markdown merge markers",
        lambda: GLDOCS_OPENING_MARKER
        in merge_markdown_output("/tmp/gitlab-docs-ci-test.md", "body"),
    )

    for fmt in ("markdown", "html", "json", "csv"):
        ok &= _check(
            f"render {fmt}",
            lambda f=fmt: bool(
                render_table(
                    DocTable(headers=["Key", "Value"], rows=[["MEGALINTER", "x"]]),
                    f,
                ).strip()
            ),
        )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
