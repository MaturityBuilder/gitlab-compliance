"""Auto-fix container images to sha256 digests in GitLab CI YAML."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ContainerImageFix:
    source_file: str
    line: int
    parent_job: str
    image_source: str
    current_image: str
    fixed_image: str


def collect_container_image_fixes(entities: dict) -> list[ContainerImageFix]:
    fixes: list[ContainerImageFix] = []
    for image in entities.get("container_images", []):
        current = str(image.get("image", "")).strip()
        digest = str(image.get("latest_digest", "")).strip()
        if not current or not digest:
            continue
        if "@sha256:" in current:
            continue
        repository_part = current.split("@sha256:", 1)[0]
        if ":" in repository_part:
            base = repository_part.rsplit(":", 1)[0]
        else:
            base = repository_part
        fixed_image = f"{base}@sha256:{digest}"
        if fixed_image == current:
            continue
        fixes.append(
            ContainerImageFix(
                source_file=str(image.get("source_file", "")),
                line=int(image.get("line", 0) or 0),
                parent_job=str(image.get("parent_job", "")),
                image_source=str(image.get("image_source", "")),
                current_image=current,
                fixed_image=fixed_image,
            )
        )
    return fixes


def _replace_image_line(line: str, current_image: str, fixed_image: str) -> str | None:
    escaped = re.escape(current_image)
    match = re.match(
        rf"^(\s*image:\s*)(['\"]?)({escaped})\2(\s*(?:#.*)?)?$",
        line.rstrip("\n"),
    )
    if not match:
        return None
    prefix, quote, _value, suffix = match.groups()
    suffix = suffix or ""
    if quote:
        result = f"{prefix}{quote}{fixed_image}{quote}{suffix}"
    else:
        result = f"{prefix}{fixed_image}{suffix}"
    return result + ("\n" if line.endswith("\n") else "")


def _replace_service_entry(line: str, current_image: str, fixed_image: str) -> str | None:
    escaped = re.escape(current_image)
    stripped = line.rstrip("\n")
    newline = "\n" if line.endswith("\n") else ""

    for pattern in (
        rf"^(\s*-\s*)(['\"]?)({escaped})\2(\s*(?:#.*)?)?$",
        rf"^(\s*name:\s*)(['\"]?)({escaped})\2(\s*(?:#.*)?)?$",
    ):
        match = re.match(pattern, stripped)
        if not match:
            continue
        prefix, quote, _value, suffix = match.groups()
        suffix = suffix or ""
        if quote:
            return f"{prefix}{quote}{fixed_image}{quote}{suffix}{newline}"
        return f"{prefix}{fixed_image}{suffix}{newline}"
    return None


def _is_service_image_line(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped.startswith("name:")


def _apply_fix_to_file(fix: ContainerImageFix, lines: list[str]) -> bool:
    if fix.line <= 0 or fix.line > len(lines):
        return False
    start = fix.line - 1
    job_header = lines[start].strip()
    if not job_header.startswith(f"{fix.parent_job}:"):
        return False
    end = min(len(lines), start + 40)
    for index in range(start, end):
        line = lines[index]
        if index > start and re.match(r"^[a-zA-Z0-9_.-]+:\s*$", line):
            break
        updated = None
        if fix.image_source == "job" and re.search(r"^\s*image:\s*", line):
            updated = _replace_image_line(line, fix.current_image, fix.fixed_image)
        elif fix.image_source == "service" and _is_service_image_line(line):
            updated = _replace_service_entry(line, fix.current_image, fix.fixed_image)
        if updated and updated != line:
            lines[index] = updated if updated.endswith("\n") else updated + "\n"
            return True
    return False


def apply_container_image_fixes(
    fixes: list[ContainerImageFix],
) -> list[ContainerImageFix]:
    applied: list[ContainerImageFix] = []
    by_file: dict[str, list[ContainerImageFix]] = {}
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
