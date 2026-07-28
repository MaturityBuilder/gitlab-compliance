"""Resolve GitLab CI job composition: extends, !reference, and script merge."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from src.modules.gitlab_reference import UnresolvedReference, resolve_reference_value

SCRIPT_KEYS = ("before_script", "script", "after_script")


def job_registry_key(source_file: str, job_name: str) -> str:
    """Stable registry key scoped to a YAML source file."""
    return f"{os.path.realpath(source_file)}::{job_name}"


def register_job_entry(
    job_registry: dict[str, dict],
    *,
    job_name: str,
    config: dict,
    source_file: str,
    line: int,
) -> None:
    """Register a job for composition and !reference resolution."""
    entry = {
        "config": config,
        "source_file": source_file,
        "line": line,
        "name": job_name,
    }
    job_registry[job_registry_key(source_file, job_name)] = entry
    # GitLab merges jobs by name; last registration wins for cross-file references.
    job_registry[job_name] = entry


@dataclass
class ScriptLine:
    """One effective script line with provenance metadata."""

    text: str
    source_file: str = ""
    source_line: int = 0
    origin: str = "direct"
    via: str = ""


@dataclass
class EffectiveJobScripts:
    """Effective script blocks for one job after composition."""

    name: str
    source_file: str
    line: int
    before_script: list[ScriptLine] = field(default_factory=list)
    script: list[ScriptLine] = field(default_factory=list)
    after_script: list[ScriptLine] = field(default_factory=list)
    extends_chain: list[str] = field(default_factory=list)
    unresolved_references: list[str] = field(default_factory=list)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_extends(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _flatten_script_items(
    value: Any,
    *,
    source_file: str,
    source_line: int,
    origin: str,
    via: str,
    unresolved: list[str],
) -> list[ScriptLine]:
    lines: list[ScriptLine] = []
    for item in _as_list(value):
        if isinstance(item, UnresolvedReference):
            unresolved.append(str(item))
            lines.append(
                ScriptLine(
                    text="",
                    source_file=source_file,
                    source_line=source_line,
                    origin="unresolved_reference",
                    via=str(item),
                )
            )
            continue
        if item is None:
            unresolved.append("!reference <unresolved>")
            lines.append(
                ScriptLine(
                    text="",
                    source_file=source_file,
                    source_line=source_line,
                    origin="unresolved_reference",
                    via="!reference <unresolved>",
                )
            )
            continue
        text = str(item)
        for offset, raw_line in enumerate(text.splitlines() or [text]):
            lines.append(
                ScriptLine(
                    text=raw_line,
                    source_file=source_file,
                    source_line=source_line + offset if source_line else 0,
                    origin=origin,
                    via=via,
                )
            )
    return lines


def _walk_extends(
    job_name: str,
    job_registry: dict[str, dict],
    *,
    seen: set[str] | None = None,
) -> list[str]:
    """Return extends chain from root parent to the job itself (exclusive of self)."""
    if seen is None:
        seen = set()
    if job_name in seen:
        raise ValueError(f"Cycle detected in extends chain involving '{job_name}'")
    seen.add(job_name)
    entry = job_registry.get(job_name)
    if not entry:
        return []
    config = entry.get("config") or {}
    parents: list[str] = []
    for parent in _normalize_extends(config.get("extends")):
        parents.extend(_walk_extends(parent, job_registry, seen=set(seen)))
        parents.append(parent)
    return parents


def _resolve_config_value(
    value: Any, job_registry: dict[str, dict], unresolved: list[str]
) -> Any:
    if isinstance(value, UnresolvedReference):
        resolved = resolve_reference_value(value, job_registry)
        if isinstance(resolved, UnresolvedReference):
            unresolved.append(str(resolved))
            return resolved
        return _resolve_config_value(resolved, job_registry, unresolved)
    if isinstance(value, list):
        return [_resolve_config_value(item, job_registry, unresolved) for item in value]
    if isinstance(value, dict):
        return {
            key: _resolve_config_value(item, job_registry, unresolved)
            for key, item in value.items()
        }
    return value


def _lookup_job_entry(
    job_registry: dict[str, dict], job_name: str, source_file: str | None = None
) -> dict:
    if source_file:
        keyed = job_registry.get(job_registry_key(source_file, job_name))
        if keyed:
            return keyed
    return job_registry.get(job_name) or {}


def compose_job_scripts(
    job_name: str,
    job_registry: dict[str, dict],
    *,
    source_file: str | None = None,
) -> EffectiveJobScripts:
    """Build effective script blocks for ``job_name`` including extends merge."""
    entry = _lookup_job_entry(job_registry, job_name, source_file)
    source_file = entry.get("source_file", "")
    line = int(entry.get("line") or 0)
    unresolved: list[str] = []
    chain = _walk_extends(job_name, job_registry)
    ordered = chain + [job_name]

    buckets: dict[str, list[ScriptLine]] = {key: [] for key in SCRIPT_KEYS}
    for name in ordered:
        if name == job_name and source_file:
            job_entry = _lookup_job_entry(job_registry, name, source_file)
        else:
            job_entry = job_registry.get(name)
        if not job_entry:
            continue
        config = job_entry.get("config") or {}
        job_file = job_entry.get("source_file", "")
        job_line = int(job_entry.get("line") or 0)
        origin = "direct" if name == job_name else "extends"
        via = "" if name == job_name else name
        for key in SCRIPT_KEYS:
            if key not in config:
                continue
            resolved = _resolve_config_value(config[key], job_registry, unresolved)
            buckets[key].extend(
                _flatten_script_items(
                    resolved,
                    source_file=job_file,
                    source_line=job_line,
                    origin=origin,
                    via=via,
                    unresolved=unresolved,
                )
            )

    return EffectiveJobScripts(
        name=job_name,
        source_file=source_file,
        line=line,
        before_script=buckets["before_script"],
        script=buckets["script"],
        after_script=buckets["after_script"],
        extends_chain=chain,
        unresolved_references=sorted(set(unresolved)),
    )


def script_lines_to_text(lines: list[ScriptLine]) -> list[str]:
    """Return non-empty script texts for entity property storage."""
    return [line.text for line in lines if line.text != "" or line.origin != "direct"]


def effective_scripts_as_values(effective: EffectiveJobScripts) -> dict[str, Any]:
    """Shape effective scripts for compliance job entity values."""
    return {
        "before_script": [line.text for line in effective.before_script],
        "script": [line.text for line in effective.script],
        "after_script": [line.text for line in effective.after_script],
        "effective_script": [
            line.text
            for line in (
                effective.before_script + effective.script + effective.after_script
            )
        ],
        "extends_chain": list(effective.extends_chain),
        "unresolved_script_references": list(effective.unresolved_references),
        "script_provenance": [
            {
                "text": line.text,
                "source_file": line.source_file,
                "source_line": line.source_line,
                "origin": line.origin,
                "via": line.via,
                "field": field,
            }
            for field, lines in (
                ("before_script", effective.before_script),
                ("script", effective.script),
                ("after_script", effective.after_script),
            )
            for line in lines
        ],
    }
