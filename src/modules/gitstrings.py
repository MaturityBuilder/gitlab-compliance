"""Render inline YAML gitstrings fences into marker-delimited markdown."""

from __future__ import annotations

import os
import re
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

import yaml

import src.properties.table_render as table_render
import src.properties.yaml_paths as yaml_paths
from src.modules.constants import (
    GITSTRINGS_MARKER_CLOSE,
    GITSTRINGS_MARKER_CLOSE_LEGACY,
    GITSTRINGS_MARKER_OPEN,
    GITSTRINGS_MARKER_OPEN_LEGACY,
)
from src.modules.doc_controller import update_marked_block
from src.modules.logging import logger

GITSTRINGS_FENCE_RE = re.compile(
    r"^```[ \t]*yaml[ \t]+gitstrings[ \t]*\r?\n(.*?)^```[ \t]*\r?$",
    re.MULTILINE | re.DOTALL,
)

DIRECTIVE_LINE_RE = re.compile(
    r"^\s*#\s*@(?P<name>[a-zA-Z0-9_-]+)(?:\s+(?P<value>.*))?\s*$"
)

CI_BLOCK_START_RE = re.compile(
    r"^\s*#\s*@(?:title|render|output(?:-file)?|sensitive)\b",
    re.IGNORECASE,
)

CI_YAML_SUFFIXES = {".yml", ".yaml"}

RENDER_MODES = frozenset({"variables", "inputs", "jobs", "includes", "include", "auto"})


def _find_git_dir(source_path: Path) -> tuple[Path | None, Path | None]:
    """Return nearest worktree root and git dir without invoking git."""
    try:
        current = source_path.resolve()
    except OSError:
        current = source_path
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        git_path = candidate / ".git"
        if git_path.is_dir():
            return candidate, git_path
        if git_path.is_file():
            try:
                text = git_path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if text.startswith("gitdir:"):
                git_dir = text.split(":", 1)[1].strip()
                resolved = (candidate / git_dir).resolve()
                return candidate, resolved
    return None, None


def _read_origin_url(git_dir: Path | None) -> str | None:
    if git_dir is None:
        return None
    config_path = git_dir / "config"
    if not config_path.is_file():
        return None
    parser = ConfigParser()
    try:
        parser.read(config_path, encoding="utf-8")
    except Exception:
        return None
    section = 'remote "origin"'
    if parser.has_option(section, "url"):
        return parser.get(section, "url")
    return None


def _read_head_ref(git_dir: Path | None) -> str | None:
    if git_dir is None:
        return None
    head_path = git_dir / "HEAD"
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if head.startswith("ref:"):
        ref_name = head.split(":", 1)[1].strip()
        prefix = "refs/heads/"
        if ref_name.startswith(prefix):
            return ref_name.removeprefix(prefix)
        return ref_name
    return head or None


def _git_ref(git_dir: Path | None, *, prefer_ci_ref: bool) -> str:
    if prefer_ci_ref:
        for env_name in ("CI_COMMIT_SHA", "CI_COMMIT_REF_NAME", "CI_DEFAULT_BRANCH"):
            value = os.environ.get(env_name)
            if value:
                return value
    git_ref = _read_head_ref(git_dir)
    if git_ref:
        return git_ref
    if not prefer_ci_ref:
        return "HEAD"
    return (
        os.environ.get("CI_COMMIT_SHA")
        or os.environ.get("CI_COMMIT_REF_NAME")
        or os.environ.get("CI_DEFAULT_BRANCH")
        or "HEAD"
    )


def _repo_url_without_credentials(repository_url: str) -> str:
    if repository_url.startswith("git@") and ":" in repository_url:
        host, path = repository_url[4:].split(":", 1)
        repository_url = f"https://{host}/{path}"

    parsed = urlsplit(repository_url)
    if parsed.scheme and parsed.netloc:
        host = parsed.hostname or parsed.netloc.rsplit("@", 1)[-1]
        if parsed.port:
            host = f"{host}:{parsed.port}"
        repository_url = urlunsplit((parsed.scheme, host, parsed.path, "", ""))

    return repository_url.removesuffix(".git").rstrip("/")


def _source_repository_url(
    source_path: Path,
) -> tuple[str | None, Path | None, Path | None, bool]:
    source_root, source_git_dir = _find_git_dir(source_path)
    current_root, _current_git_dir = _find_git_dir(Path.cwd())
    is_current_repo = (
        source_root is not None
        and current_root is not None
        and source_root == current_root
    )

    if is_current_repo and os.environ.get("CI_REPOSITORY_URL"):
        return os.environ["CI_REPOSITORY_URL"], source_root, source_git_dir, True

    remote_url = _read_origin_url(source_git_dir)
    if remote_url:
        return remote_url, source_root, source_git_dir, False

    if os.environ.get("CI_REPOSITORY_URL"):
        return os.environ["CI_REPOSITORY_URL"], source_root, source_git_dir, True

    return None, source_root, source_git_dir, False


def _blob_url(
    repository_url: str,
    *,
    ref: str,
    relative_path: str,
    start_line: int,
    end_line: int | None,
) -> str:
    repo_url = _repo_url_without_credentials(repository_url)
    parsed = urlsplit(repo_url)
    blob_segment = "/blob/"
    if parsed.hostname and "gitlab" in parsed.hostname.casefold():
        blob_segment = "/-/blob/"

    line_fragment = f"L{start_line}"
    if end_line and end_line > start_line:
        if parsed.hostname and "gitlab" in parsed.hostname.casefold():
            line_fragment += f"-{end_line}"
        else:
            line_fragment += f"-L{end_line}"

    encoded_ref = quote(ref, safe="")
    encoded_path = quote(relative_path, safe="/._-")
    return f"{repo_url}{blob_segment}{encoded_ref}/{encoded_path}#{line_fragment}"


@dataclass
class GitstringsDirectives:
    title: str | None = None
    render: str = "auto"
    description: str | None = None
    output: str | None = None
    sensitive: list[str] = field(default_factory=list)


@dataclass
class GitstringsBlock:
    raw_body: str
    cleaned_yaml: str
    directives: GitstringsDirectives = field(default_factory=GitstringsDirectives)
    source_fence: str = ""
    source_start_line: int | None = None
    source_end_line: int | None = None


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
            raw = (value or "auto").strip()
            if "." not in raw and raw.lower() in RENDER_MODES:
                lowered = raw.lower()
                directives.render = "includes" if lowered == "include" else lowered
            else:
                directives.render = raw or "auto"
        elif name == "sensitive":
            directives.sensitive.extend(yaml_paths.parse_path_list(value))
        elif name in ("output", "output_file"):
            directives.output = value or None
        elif name == "description":
            directives.description = value or None

        index += 1

    cleaned = "\n".join(yaml_lines).strip()
    return directives, cleaned


def _directive_prefix_lines(raw_block: str) -> list[str]:
    """Lines at the start of a gitstrings block that are @directives (not YAML)."""
    prefix: list[str] = []
    lines = raw_block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = DIRECTIVE_LINE_RE.match(line)
        if not match:
            break

        name = match.group("name").lower().replace("-", "_")
        value = (match.group("value") or "").strip()
        prefix.append(line)
        index += 1

        if name == "description" and not value:
            while index < len(lines):
                next_line = lines[index]
                if DIRECTIVE_LINE_RE.match(next_line):
                    break
                if next_line.strip().startswith("#"):
                    prefix.append(next_line)
                    index += 1
                    continue
                break

    return prefix


def _masked_source_yaml_body(block: GitstringsBlock, doc: dict) -> str:
    """Source YAML for keep_source, with @sensitive paths redacted."""
    sensitive = block.directives.sensitive
    if not sensitive:
        return block.raw_body.rstrip()

    masked_doc = yaml_paths.mask_sensitive_in_structure(doc, "", sensitive)
    masked_cleaned = yaml.dump(
        masked_doc,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    ).rstrip("\n")

    prefix_lines = _directive_prefix_lines(block.raw_body)
    if prefix_lines:
        return "\n".join(prefix_lines + [masked_cleaned])
    return masked_cleaned


def extract_gitstrings_blocks(markdown_text: str) -> list[GitstringsBlock]:
    blocks: list[GitstringsBlock] = []
    for match in GITSTRINGS_FENCE_RE.finditer(markdown_text):
        body = match.group(1)
        directives, cleaned = parse_directives(body)
        start_line = markdown_text.count("\n", 0, match.start()) + 1
        end_line = markdown_text.count("\n", 0, match.end()) + 1
        blocks.append(
            GitstringsBlock(
                raw_body=body.rstrip("\n"),
                cleaned_yaml=cleaned,
                directives=directives,
                source_fence=match.group(0),
                source_start_line=start_line,
                source_end_line=end_line,
            )
        )
    return blocks


def _collect_yaml_body_lines(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect YAML lines for one decorated fragment (single top-level key)."""
    body: list[str] = []
    i = start
    root_key: str | None = None
    top_level_key_re = re.compile(r"^[\w.*][\w.*-]*:")
    while i < len(lines):
        line = lines[i]
        if CI_BLOCK_START_RE.match(line):
            break
        if line.strip() == "---":
            break
        stripped = line.strip()
        if not stripped:
            body.append(line)
            i += 1
            continue
        if stripped.startswith("#") and not DIRECTIVE_LINE_RE.match(line):
            body.append(line)
            i += 1
            continue
        if DIRECTIVE_LINE_RE.match(line):
            break
        if top_level_key_re.match(line) and not line.startswith((" ", "\t")):
            if root_key is None:
                root_key = line.split(":", 1)[0].strip()
                body.append(line)
                i += 1
                continue
            break
        body.append(line)
        i += 1
    return body, i


def _split_ci_decorated_block(
    lines: list[str], start: int
) -> tuple[list[str], list[str], int] | None:
    """Return directive lines, yaml lines, and index after the block."""
    idx = start
    if idx >= len(lines) or not CI_BLOCK_START_RE.match(lines[idx]):
        return None

    header: list[str] = []
    while idx < len(lines):
        line = lines[idx]
        match = DIRECTIVE_LINE_RE.match(line)
        if not match:
            break
        header.append(line)
        idx += 1
        name = match.group("name").lower().replace("-", "_")
        value = (match.group("value") or "").strip()
        if name == "description" and not value:
            while idx < len(lines):
                next_line = lines[idx]
                if DIRECTIVE_LINE_RE.match(next_line):
                    break
                if next_line.strip().startswith("#"):
                    header.append(next_line)
                    idx += 1
                    continue
                break

    yaml_lines, end_idx = _collect_yaml_body_lines(lines, idx)
    if not header and not yaml_lines:
        return None
    return header, yaml_lines, end_idx


def extract_gitstrings_blocks_from_ci_yaml(text: str) -> list[GitstringsBlock]:
    """Find `# @title` / `# @render` / `# @output` decorated sections in CI YAML."""
    lines = text.splitlines()
    blocks: list[GitstringsBlock] = []
    index = 0
    while index < len(lines):
        if not CI_BLOCK_START_RE.match(lines[index]):
            index += 1
            continue
        split = _split_ci_decorated_block(lines, index)
        if split is None:
            index += 1
            continue
        header, yaml_lines, end_idx = split
        raw_body = "\n".join(header + yaml_lines).strip()
        if not raw_body:
            index = end_idx
            continue
        directives, cleaned = parse_directives(raw_body)
        blocks.append(
            GitstringsBlock(
                raw_body=raw_body,
                cleaned_yaml=cleaned,
                directives=directives,
                source_start_line=index + 1,
                source_end_line=end_idx,
            )
        )
        index = end_idx if end_idx > index else index + 1
    return blocks


def extract_gitstrings_blocks_from_file(scan_path: str | Path) -> list[GitstringsBlock]:
    path = Path(scan_path)
    text = path.read_text(encoding="utf-8")
    blocks = extract_gitstrings_blocks(text)
    if blocks:
        return blocks
    if path.suffix.lower() in CI_YAML_SUFFIXES:
        ci_blocks = extract_gitstrings_blocks_from_ci_yaml(text)
        if ci_blocks:
            return ci_blocks
    return []


def resolve_fragment_output(
    directives: GitstringsDirectives,
    default_output_path: str | Path,
    scan_path: str | Path,
    *,
    honor_fragment_output: bool = True,
) -> Path:
    """Resolve marker file for one fragment.

    When ``honor_fragment_output`` is false (CLI ``-o`` / ``--output`` was set),
    ``# @output`` on the fragment is ignored and ``default_output_path`` is used.
    """
    if honor_fragment_output and directives.output:
        base = Path(scan_path).resolve().parent
        return (base / directives.output).resolve()
    return Path(default_output_path).resolve()


def _looks_like_jobs_map(doc: dict) -> bool:
    job_keys = {"stage", "script", "extends", "image", "rules"}
    dict_values = [v for v in doc.values() if isinstance(v, dict)]
    if not dict_values:
        return False
    return all(job_keys & set(v.keys()) for v in dict_values)


def _load_yaml_root(text: str) -> object:
    """Load YAML that may contain one or more documents.

    GitLab CI component files commonly use a first YAML document for ``spec:``
    inputs followed by ``---`` and the actual pipeline body. PyYAML's
    ``safe_load`` raises ``ComposerError`` for that shape, so load all documents
    and merge mapping documents into a single root for path/table rendering.
    """
    documents = [
        document for document in yaml.safe_load_all(text) if document is not None
    ]
    if not documents:
        return {}
    if len(documents) == 1:
        return documents[0]

    if all(isinstance(document, dict) for document in documents):
        merged: dict = {}
        for document in documents:
            merged.update(document)
        return merged

    return {"documents": documents}


def _load_pipeline_root(scan_path: str | Path, fragment_doc: dict) -> dict:
    path = Path(scan_path)
    if path.suffix.lower() in CI_YAML_SUFFIXES and path.is_file():
        try:
            loaded = _load_yaml_root(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return loaded
        except (OSError, yaml.YAMLError) as exc:
            logger.trace(exc)
    return fragment_doc


def detect_render_mode(doc: object, directive_render: str) -> str:
    mode = yaml_paths.normalize_legacy_render(directive_render)
    if (directive_render or "auto") != "auto" and not yaml_paths.is_legacy_render_mode(
        directive_render
    ):
        return "path"
    if mode != "auto":
        return mode
    if not isinstance(doc, dict):
        return "auto"
    spec = doc.get("spec")
    if isinstance(spec, dict) and "inputs" in spec:
        return "inputs"
    if "variables" in doc:
        return "variables"
    if "include" in doc:
        return "includes"
    if _looks_like_jobs_map(doc):
        return "jobs"
    return "auto"


def _ci_yaml_path(scan_path: str | Path | None) -> Path | None:
    if scan_path is None:
        return None
    path = Path(scan_path)
    if path.suffix.lower() in CI_YAML_SUFFIXES and path.is_file():
        return path
    return None


def _render_includes_markdown(
    doc: dict,
    *,
    config_file: str,
    scan_path: str | Path | None,
    include_nested: bool,
) -> str:
    """Render includes; nested expansion is local-on-disk only (see docs)."""
    ci = _ci_yaml_path(scan_path)
    if include_nested and ci is not None:
        return table_render.render_includes_from_config(str(ci), include_nested=True)
    entries = doc.get("include") or []
    return table_render.render_includes_table(
        entries,
        config_file=config_file or (str(ci) if ci else ""),
    )


def _render_table_for_doc(
    doc: dict,
    mode: str,
    *,
    sensitive_paths: list[str] | None = None,
    config_file: str = "",
    scan_path: str | Path | None = None,
    include_nested: bool = False,
) -> str:
    if mode == "auto":
        mode = detect_render_mode(doc, "auto")
    if mode == "inputs":
        spec = doc.get("spec") or {}
        inputs = spec.get("inputs") or {}
        return table_render.render_inputs_table(
            inputs,
            path_prefix="spec.inputs",
            sensitive_paths=sensitive_paths,
        )
    if mode == "variables":
        variables = doc.get("variables") or {}
        return table_render.render_variables_table(
            variables,
            path_prefix="variables",
            sensitive_paths=sensitive_paths,
        )
    if mode == "includes":
        return _render_includes_markdown(
            doc,
            config_file=config_file,
            scan_path=scan_path,
            include_nested=include_nested,
        )
    if mode == "jobs":
        return table_render.render_jobs_table(doc)
    return table_render.render_generic_kv_table(doc, sensitive_paths=sensitive_paths)


def _render_path_specs(
    root: dict,
    render_spec: str,
    *,
    sensitive_paths: list[str] | None = None,
    config_file: str = "",
    scan_path: str | Path | None = None,
    include_nested: bool = False,
) -> str:
    parts: list[str] = []
    for path_spec in yaml_paths.parse_path_list(render_spec):
        rendered = table_render.render_path_markdown(
            root,
            path_spec,
            sensitive_paths=sensitive_paths,
            config_file=config_file,
            include_nested=include_nested,
            scan_path=scan_path,
        )
        if rendered.strip():
            parts.append(rendered.strip())
    return "\n\n".join(parts)


def _count_variables_for_path(root: dict, path_spec: str) -> int:
    node = yaml_paths.resolve_yaml_path(root, path_spec)
    if node is None:
        return 0
    segments = [segment for segment in path_spec.split(".") if segment]
    last = segments[-1] if segments else ""

    if last == "variables" and isinstance(node, dict):
        return len(node)
    if ".variables." in path_spec:
        return 1
    if isinstance(node, dict):
        variables = node.get("variables")
        if isinstance(variables, dict):
            return len(variables)
    return 0


def _limited_render_note(root: dict, render_spec: str) -> str:
    if yaml_paths.is_legacy_render_mode(render_spec) or render_spec == "auto":
        return ""
    rendered_paths = yaml_paths.parse_path_list(render_spec)
    if not rendered_paths:
        return ""

    variable_count = sum(
        _count_variables_for_path(root, path_spec) for path_spec in rendered_paths
    )
    path_text = ", ".join(f"`{path_spec}`" for path_spec in rendered_paths)
    note = f"> Limited render: only {path_text} are included in this section."
    if variable_count:
        suffix = "variable" if variable_count == 1 else "variables"
        note += f" Selected variable count: {variable_count} {suffix}."
    return note + "\n"


def _source_code_link(
    block: GitstringsBlock,
    *,
    scan_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> str:
    if scan_path is None or block.source_start_line is None:
        return ""

    source_path = Path(scan_path)
    (
        repository_url,
        repository_root,
        repository_git_dir,
        prefer_ci_ref,
    ) = _source_repository_url(source_path)
    if repository_root is not None:
        try:
            relative = source_path.resolve().relative_to(repository_root)
        except ValueError:
            relative = source_path.name
    elif output_path is not None:
        try:
            relative = os.path.relpath(
                source_path.resolve(),
                start=Path(output_path).resolve().parent,
            )
        except (OSError, ValueError):
            relative = source_path.name
    else:
        relative = source_path.name

    relative = str(relative).replace(os.sep, "/")
    line_fragment = f"#L{block.source_start_line}"
    if block.source_end_line and block.source_end_line > block.source_start_line:
        line_fragment += f"-L{block.source_end_line}"
    if repository_url:
        href = _blob_url(
            repository_url,
            ref=_git_ref(repository_git_dir, prefer_ci_ref=prefer_ci_ref),
            relative_path=relative,
            start_line=block.source_start_line,
            end_line=block.source_end_line,
        )
    else:
        href = quote(relative, safe="/._-") + line_fragment
    label = f"`{relative}`"
    if block.source_end_line and block.source_end_line > block.source_start_line:
        label += f" lines {block.source_start_line}-{block.source_end_line}"
    else:
        label += f" line {block.source_start_line}"
    return f"> Source: [{label}]({href})\n"


def render_fragment(
    block: GitstringsBlock,
    *,
    keep_source: bool = True,
    scan_path: str | Path | None = None,
    output_path: str | Path | None = None,
    include_nested: bool = False,
) -> str:
    parts: list[str] = []
    directives = block.directives

    if directives.title:
        parts.append(f"## {directives.title}\n")

    doc = _load_yaml_root(block.cleaned_yaml) if block.cleaned_yaml else {}
    if doc is None:
        doc = {}
    if not isinstance(doc, dict):
        doc = {"value": doc}

    pipeline_root = doc
    config_file = str(scan_path) if scan_path is not None else ""
    if scan_path is not None:
        pipeline_root = _load_pipeline_root(scan_path, doc)

    render_spec = directives.render or "auto"
    if directives.description:
        for paragraph in directives.description.split("\n\n"):
            paragraph = paragraph.strip()
            if paragraph:
                parts.append(paragraph + "\n")
    source_link = _source_code_link(
        block,
        scan_path=scan_path,
        output_path=output_path,
    )
    if source_link:
        parts.append(source_link)
    limited_note = _limited_render_note(pipeline_root, render_spec)
    if limited_note:
        parts.append(limited_note)

    if yaml_paths.is_legacy_render_mode(render_spec) or render_spec == "auto":
        mode = detect_render_mode(doc, render_spec)
        if mode == "path":
            parts.append(
                _render_path_specs(
                    pipeline_root,
                    render_spec,
                    sensitive_paths=directives.sensitive,
                    config_file=config_file,
                    scan_path=scan_path,
                    include_nested=include_nested,
                )
            )
        else:
            parts.append(
                _render_table_for_doc(
                    doc,
                    mode,
                    sensitive_paths=directives.sensitive,
                    config_file=config_file,
                    scan_path=scan_path,
                    include_nested=include_nested,
                )
            )
    else:
        parts.append(
            _render_path_specs(
                pipeline_root,
                render_spec,
                sensitive_paths=directives.sensitive,
                config_file=config_file,
                scan_path=scan_path,
                include_nested=include_nested,
            )
        )
    parts.append("")

    if keep_source:
        parts.append("<details>")
        parts.append("<summary>Source YAML</summary>")
        parts.append("")
        parts.append("```yaml")
        parts.append(_masked_source_yaml_body(block, doc))
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
    honor_fragment_output: bool = True,
    include_nested: bool = False,
) -> dict[Path, str]:
    grouped: dict[Path, list[str]] = {}
    for block in blocks:
        target = resolve_fragment_output(
            block.directives,
            default_output_path,
            scan_path,
            honor_fragment_output=honor_fragment_output,
        )
        rendered = render_fragment(
            block,
            keep_source=keep_source,
            scan_path=scan_path,
            output_path=target,
            include_nested=include_nested,
        )
        grouped.setdefault(target, []).append(rendered)
    return {
        path: "\n".join(sections).strip() + "\n" for path, sections in grouped.items()
    }


def _upgrade_legacy_gitstrings_markers(path: Path) -> None:
    """Replace reference-style markers (visible in some renderers) with HTML comments."""
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    updated = text.replace(GITSTRINGS_MARKER_OPEN_LEGACY, GITSTRINGS_MARKER_OPEN)
    updated = updated.replace(GITSTRINGS_MARKER_CLOSE_LEGACY, GITSTRINGS_MARKER_CLOSE)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def write_gitstrings_block(
    target_path: str | Path,
    content: str,
    *,
    dry: bool = False,
) -> None:
    path = Path(target_path)
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        _upgrade_legacy_gitstrings_markers(path)
    update_marked_block(
        file_path=str(path),
        content=content,
        marker_start=GITSTRINGS_MARKER_OPEN,
        marker_end=GITSTRINGS_MARKER_CLOSE,
        dry=dry,
    )


def _default_gitstrings_output(scan_path: Path, output_file: str | Path | None) -> Path:
    if output_file:
        return Path(output_file)
    if scan_path.suffix.lower() in CI_YAML_SUFFIXES:
        return scan_path.parent / "README.md"
    return scan_path


def process_gitstrings(
    input_file: str | Path,
    output_file: str | Path | None = None,
    *,
    dry: bool = False,
    keep_source: bool = True,
    include_nested: bool = False,
) -> list[Path]:
    scan_path = Path(input_file)
    default_output = _default_gitstrings_output(scan_path, output_file)
    honor_fragment_output = output_file is None
    blocks = extract_gitstrings_blocks_from_file(scan_path)
    if not blocks:
        logger.info(
            f"No gitstrings decorators or ```yaml gitstrings fences found in {scan_path}"
        )
        return []

    by_output = render_gitstrings_by_output(
        blocks,
        default_output_path=default_output,
        scan_path=scan_path,
        keep_source=keep_source,
        honor_fragment_output=honor_fragment_output,
        include_nested=include_nested,
    )
    written: list[Path] = []
    for target_path, markdown in by_output.items():
        logger.info(f"Updating gitstrings markers in {target_path}")
        write_gitstrings_block(target_path, markdown, dry=dry)
        written.append(target_path)
    return written
