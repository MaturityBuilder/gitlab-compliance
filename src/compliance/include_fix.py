"""Auto-fix outdated include refs in GitLab CI YAML."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class IncludeVersionFix:
    source_file: str
    line: int
    include_type: str
    project: str
    current_version: str
    latest_version: str


def collect_include_version_fixes(entities: dict) -> list[IncludeVersionFix]:
    fixes: list[IncludeVersionFix] = []
    for include in entities.get("includes", []):
        include_type = include.get("include_type", "")
        if include_type not in {"project", "component"}:
            continue
        latest = str(include.get("latest_version", "")).strip()
        current = str(include.get("version", "")).strip()
        if not latest or not include.get("update_available"):
            continue
        if current == latest:
            continue
        fixes.append(
            IncludeVersionFix(
                source_file=include.get("source_file", ""),
                line=int(include.get("line", 0) or 0),
                include_type=include_type,
                project=str(include.get("project", "")),
                current_version=current,
                latest_version=latest,
            )
        )
    return fixes


def _replace_ref_line(line: str, latest_version: str) -> str | None:
    match = re.match(r"^(\s*ref:\s*)(['\"]?)([^'\"#\n]+)\2\s*(#.*)?$", line)
    if not match:
        return None
    prefix, quote, _value, suffix = match.groups()
    suffix = suffix or ""
    if quote:
        return f"{prefix}{quote}{latest_version}{quote}{suffix}\n"
    return f"{prefix}{latest_version}{suffix}\n"


def _replace_component_line(
    line: str, current_version: str, latest_version: str
) -> str | None:
    if "component:" not in line and "component :" not in line:
        return None
    pattern = re.compile(
        rf"(@{re.escape(current_version)})(?=(['\"\s#]|$))",
        re.IGNORECASE,
    )
    if not pattern.search(line):
        return None
    return pattern.sub(f"@{latest_version}", line, count=1)


def _apply_fix_to_file(fix: IncludeVersionFix, lines: list[str]) -> bool:
    if fix.line <= 0 or fix.line > len(lines):
        return False
    start = fix.line - 1
    end = min(len(lines), start + 12)
    for index in range(start, end):
        line = lines[index]
        if index > start and re.match(r"^\s*-\s+", line):
            break
        updated = None
        if fix.include_type == "project":
            updated = _replace_ref_line(line, fix.latest_version)
        elif fix.include_type == "component":
            updated = _replace_component_line(
                line, fix.current_version, fix.latest_version
            )
        if updated and updated != line:
            lines[index] = updated if updated.endswith("\n") else updated + "\n"
            return True
    return False


def apply_include_version_fixes(
    fixes: list[IncludeVersionFix],
) -> list[IncludeVersionFix]:
    applied: list[IncludeVersionFix] = []
    by_file: dict[str, list[IncludeVersionFix]] = {}
    for fix in fixes:
        if not fix.source_file:
            continue
        by_file.setdefault(fix.source_file, []).append(fix)

    for source_file, file_fixes in by_file.items():
        with open(source_file, encoding="utf-8") as handle:
            lines = handle.readlines()
        changed = False
        for fix in file_fixes:
            if _apply_fix_to_file(fix, lines):
                applied.append(fix)
                changed = True
        if changed:
            with open(source_file, "w", encoding="utf-8") as handle:
                handle.writelines(lines)
    return applied
