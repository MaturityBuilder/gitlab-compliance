#!/usr/bin/env python3
"""Wrap prose in docs markdown to 80 columns; align tables; add fence languages."""
from __future__ import annotations

from pathlib import Path


def wrap_line(line: str, width: int = 80) -> list[str]:
    if len(line) <= width or not line.strip():
        return [line]
    stripped = line.lstrip()
    if stripped.startswith(("#", "|", "```", "<!--", "> ")):
        return [line]
    indent = line[: len(line) - len(stripped)]
    prefix, body, cont = "", stripped, ""
    if stripped.startswith("- "):
        prefix, body, cont = "- ", stripped[2:], "  "
    elif stripped.startswith("* "):
        prefix, body, cont = "* ", stripped[2:], "  "
    words, cur, out = body.split(), "", []
    limit = width - len(indent) - len(prefix)
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= limit:
            cur += " " + word
        else:
            out.append(indent + prefix + cur)
            prefix, cur = cont, word
    if cur:
        out.append(indent + prefix + cur)
    return out or [line]


def fix_fences(lines: list[str]) -> list[str]:
    out, in_fence = [], False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            if not in_fence:
                if line.strip() == "```":
                    nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    lang = "text"
                    if nxt.startswith(("$", "poetry", "pip", "docker", "gitlab-compliance", "cp ")):
                        lang = "bash"
                    elif "Scenario:" in nxt or nxt.startswith("Given"):
                        lang = "gherkin"
                    line = f"```{lang}"
                in_fence = True
            else:
                in_fence = False
        out.append(line)
    return out


def align_table(block: list[str]) -> list[str]:
    rows = [[c.strip() for c in ln.strip("|").split("|")] for ln in block]
    data = [r for r in rows if r and not all(set(c) <= set("-: ") for c in r)]
    if not data:
        return block
    cols = max(len(r) for r in data)
    widths = [0] * cols
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row: list[str]) -> str:
        cells = row + [""] * (cols - len(row))
        return "|" + "|".join(f" {cells[i]:<{widths[i]}} " for i in range(cols)) + "|"

    sep = "|" + "|".join(f" {'-' * w} " for w in widths) + "|"
    return [fmt(data[0]), sep] + [fmt(r) for r in data[1:]]




def table_to_list(block: list[str]) -> list[str]:
    rows = [[c.strip() for c in ln.strip("|").split("|")] for ln in block]
    data = [r for r in rows if r and not all(set(c) <= set("-: ") for c in r)]
    if not data:
        return block
    header, body = data[0], data[1:]
    out = [""]
    for row in body:
        label = row[0] if row else ""
        rest = " — ".join(row[1:]) if len(row) > 1 else ""
        line = f"- **{label}:** {rest}".strip()
        if len(line) <= 80:
            out.append(line)
        else:
            out.append(f"- **{label}:**")
            for cell in row[1:]:
                out.append(f"  - {cell}")
    out.append("")
    return out

def process(text: str) -> str:
    lines = fix_fences(text.splitlines())
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            aligned = align_table(block)
            if any(len(ln) > 80 for ln in aligned):
                out.extend(table_to_list(block))
            else:
                for ln in aligned:
                    out.extend(wrap_line(ln))
            continue
        out.extend(wrap_line(lines[i]))
        i += 1
    cleaned: list[str] = []
    for ln in out:
        if ln == "" and cleaned and cleaned[-1] == "":
            continue
        cleaned.append(ln.rstrip())
    return "\n".join(cleaned) + "\n"


def main() -> None:
    targets = list(Path("docs").rglob("*.md"))
    targets.append(Path("examples/example-github-actions/README.md"))
    for path in targets:
        if path.exists():
            path.write_text(process(path.read_text(encoding="utf-8")), encoding="utf-8")
            print(path)


if __name__ == "__main__":
    main()
