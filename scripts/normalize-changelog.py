#!/usr/bin/env python3
"""Normalize CHANGELOG.md for markdownlint (version-scoped headings, wrap lines)."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def normalize(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    version = ""
    for line in lines:
        match = re.match(r"^## \[(.+?)\]", line)
        if match:
            version = match.group(1)
        if line.startswith("### Bug Fixes"):
            line = f"### Bug Fixes ({version})" if version else line
        if line.startswith("### Features"):
            line = f"### Features ({version})" if version else line
        if line.startswith("### ⚠ BREAKING CHANGES"):
            line = f"### BREAKING CHANGES ({version})" if version else "### BREAKING CHANGES"
        if line.startswith("* ") and len(line) > 80:
            prefix = "* "
            body = line[2:]
            while len(body) > 78:
                cut = body.rfind(" ", 0, 78)
                if cut <= 0:
                    cut = 78
                out.append(prefix + body[:cut])
                body = body[cut:].lstrip()
                prefix = "  "
            out.append(prefix + body)
            continue
        if line == "" and out and out[-1] == "":
            continue
        out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "CHANGELOG.md")
    normalize(target)
