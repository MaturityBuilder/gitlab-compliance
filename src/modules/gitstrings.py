"""Render inline YAML gitstrings fences into marker-delimited markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import src.properties.table_render as table_render
from src.modules.constants import GITSTRINGS_MARKER_CLOSE, GITSTRINGS_MARKER_OPEN
from src.modules.doc_controller import update_marked_block
from src.modules.logging import logger

GITSTRINGS_FENCE_RE = re.compile(
    r"^```[ \t]*yaml[ \t]+gitstrings[ \t]*\r?\n(.*?)^```[ \t]*\r?$",
    re.MULTILINE | re.DOTALL,
)

DIRECTIVE_LINE_RE = re.compile(
    r"^\s*#\s*@(?P<name>[a-zA-Z0-9_-]+)(?:\s+(?P<value>.*))?\s*$"
)

RENDER_MODES = frozenset({"variables", "inputs", "jobs", "auto"})


@dataclass
class GitstringsDirectives:
    title: str | None = None
    render: str = "auto"
    description: str | None = None
    output: str | None = None


@dataclass
class GitstringsBlock:
    raw_body: str
    cleaned_yaml: str
    directives: GitstringsDirectives = field(default_factory=GitstringsDirectives)
    source_fence: str = ""


def parse_directives(raw_block: str) -> tuple[GitstringsDirectives, str]:
    directives = GitstringsDirectives()
    yaml_lines: list[str] = []
    lines = raw_block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = DIRECTIVE_LINE_RE.match(line)
        if not match:
            yaml_lines.append(line)
            index += 1
            continue

        name = match.group("name").lower().replace("-", "_")
        value = (match.group("value") or "").strip()

        if name == "description" and not value:
            prose_lines: list[str] = []
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if DIRECTIVE_LINE_RE.match(next_line):
                    break
                if next_line.strip().startswith("#"):
                    prose = next_line.strip()
                    if prose.startswith("#"):
                        prose = prose[1:].lstrip()
                    prose_lines.append(prose)
                    index += 1
                    continue
                break
            directives.description = "\n".join(prose_lines).strip() or None
            continue

        if name == "title":
            directives.title = value or None
        elif name == "render":
            directives.render = value.lower() if value else "auto"
        elif name in ("output", "output_file"):
            directives.output = value or None
        elif name == "description":
            directives.description = value or None

        index += 1

    cleaned = "\n".join(yaml_lines).strip()
    return directives, cleaned


def extract_gitstrings_blocks(markdown_text: str) -> list[GitstringsBlock]:
    blocks: list[GitstringsBlock] = []
    for match in GITSTRINGS_FENCE_RE.finditer(markdown_text):
        body = match.group(1)
        directives, cleaned = parse_directives(body)
        blocks.append(
            GitstringsBlock(
                raw_body=body.rstrip("\n"),
                cleaned_yaml=cleaned,
                directives=directives,
                source_fence=match.group(0),
            )
        )
    return blocks


def extract_gitstrings_blocks_from_file(scan_path: str | Path) -> list[GitstringsBlock]:
    text = Path(scan_path).read_text(encoding="utf-8")
    return extract_gitstrings_blocks(text)


def resolve_fragment_output(
    directives: GitstringsDirectives,
    default_output_path: str | Path,
    scan_path: str | Path,
) -> Path:
    if directives.output:
        base = Path(scan_path).resolve().parent
        return (base / directives.output).resolve()
    return Path(default_output_path).resolve()


def _looks_like_jobs_map(doc: dict) -> bool:
    job_keys = {"stage", "script", "extends", "image", "rules"}
    dict_values = [v for v in doc.values() if isinstance(v, dict)]
    if not dict_values:
        return False
    return all(job_keys & set(v.keys()) for v in dict_values)


def detect_render_mode(doc: object, directive_render: str) -> str:
    mode = (directive_render or "auto").lower()
    if mode != "auto":
        return mode if mode in RENDER_MODES else "auto"
    if not isinstance(doc, dict):
        return "auto"
    spec = doc.get("spec")
    if isinstance(spec, dict) and "inputs" in spec:
        return "inputs"
    if "variables" in doc:
        return "variables"
    if _looks_like_jobs_map(doc):
        return "jobs"
    return "auto"


def _render_table_for_doc(doc: dict, mode: str) -> str:
    if mode == "auto":
        mode = detect_render_mode(doc, "auto")
    if mode == "inputs":
        spec = doc.get("spec") or {}
        inputs = spec.get("inputs") or {}
        return table_render.render_inputs_table(inputs)
    if mode == "variables":
        variables = doc.get("variables") or {}
        return table_render.render_variables_table(variables)
    if mode == "jobs":
        return table_render.render_jobs_table(doc)
    return table_render.render_generic_kv_table(doc)


def render_fragment(
    block: GitstringsBlock,
    *,
    keep_source: bool = True,
) -> str:
    parts: list[str] = []
    directives = block.directives

    if directives.title:
        parts.append(f"## {directives.title}\n")
    if directives.description:
        for paragraph in directives.description.split("\n\n"):
            paragraph = paragraph.strip()
            if paragraph:
                parts.append(paragraph + "\n")

    doc = yaml.safe_load(block.cleaned_yaml) if block.cleaned_yaml else {}
    if doc is None:
        doc = {}
    if not isinstance(doc, dict):
        doc = {"value": doc}

    mode = detect_render_mode(doc, directives.render)
    parts.append(_render_table_for_doc(doc, mode))
    parts.append("")

    if keep_source:
        parts.append("<details>")
        parts.append("<summary>Source YAML</summary>")
        parts.append("")
        parts.append("```yaml")
        parts.append(block.raw_body.rstrip())
        parts.append("```")
        parts.append("</details>")
        parts.append("")

    return "\n".join(parts).strip() + "\n"


def render_gitstrings_by_output(
    blocks: list[GitstringsBlock],
    *,
    default_output_path: str | Path,
    scan_path: str | Path,
    keep_source: bool = True,
) -> dict[Path, str]:
    grouped: dict[Path, list[str]] = {}
    for block in blocks:
        target = resolve_fragment_output(
            block.directives, default_output_path, scan_path
        )
        rendered = render_fragment(block, keep_source=keep_source)
        grouped.setdefault(target, []).append(rendered)
    return {path: "\n".join(sections).strip() + "\n" for path, sections in grouped.items()}


def write_gitstrings_block(
    target_path: str | Path,
    content: str,
    *,
    dry: bool = False,
) -> None:
    path = Path(target_path)
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
    update_marked_block(
        file_path=str(path),
        content=content,
        marker_start=GITSTRINGS_MARKER_OPEN,
        marker_end=GITSTRINGS_MARKER_CLOSE,
        dry=dry,
    )


def process_gitstrings(
    input_file: str | Path,
    output_file: str | Path | None = None,
    *,
    dry: bool = False,
    keep_source: bool = True,
) -> list[Path]:
    scan_path = Path(input_file)
    default_output = Path(output_file) if output_file else scan_path
    blocks = extract_gitstrings_blocks_from_file(scan_path)
    if not blocks:
        logger.info(f"No ```yaml gitstrings fences found in {scan_path}")
        return []

    by_output = render_gitstrings_by_output(
        blocks,
        default_output_path=default_output,
        scan_path=scan_path,
        keep_source=keep_source,
    )
    written: list[Path] = []
    for target_path, markdown in by_output.items():
        logger.info(f"Updating gitstrings markers in {target_path}")
        write_gitstrings_block(target_path, markdown, dry=dry)
        written.append(target_path)
    return written
