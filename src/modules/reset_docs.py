"""Merge generated documentation into markdown output files."""

from pathlib import Path

from src.modules.constants import GLDOCS_CLOSING_MARKER, GLDOCS_OPENING_MARKER


def strip_generation_markers(content: str) -> str:
    """Remove opening/closing markers and any prior generated block between them."""
    if GLDOCS_OPENING_MARKER not in content:
        return content
    start = content.find(GLDOCS_OPENING_MARKER)
    end = content.rfind(GLDOCS_CLOSING_MARKER)
    if end == -1 or end < start:
        return content[:start] + content[start + len(GLDOCS_OPENING_MARKER) :]
    before = content[:start]
    after = content[end + len(GLDOCS_CLOSING_MARKER) :]
    return before + after


def merge_markdown_output(output_file: str | Path, body: str) -> str:
    """
    Insert or replace generated body between gitlab-docs HTML comment markers.
    """
    path = Path(output_file)
    body = body.strip()
    wrapped_body = (
        f"{GLDOCS_OPENING_MARKER}\n\n{body}\n\n{GLDOCS_CLOSING_MARKER}\n"
    )

    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        if GLDOCS_OPENING_MARKER in existing and GLDOCS_CLOSING_MARKER in existing:
            start = existing.find(GLDOCS_OPENING_MARKER)
            end = existing.rfind(GLDOCS_CLOSING_MARKER) + len(GLDOCS_CLOSING_MARKER)
            return existing[:start] + wrapped_body.strip() + existing[end:]
        cleaned = strip_generation_markers(existing).rstrip()
        if cleaned:
            return f"{cleaned}\n\n{wrapped_body}"
        return wrapped_body

    return wrapped_body


def write_documentation(
    output_file: str | Path,
    body: str,
    output_format: str = "markdown",
) -> None:
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "markdown":
        path.write_text(merge_markdown_output(path, body), encoding="utf-8")
    else:
        path.write_text(body.strip() + "\n", encoding="utf-8")
