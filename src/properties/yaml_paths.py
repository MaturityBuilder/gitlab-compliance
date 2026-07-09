"""Dot-path navigation and gitstrings render/sensitive path helpers."""

from __future__ import annotations

from typing import Any

LEGACY_RENDER_MODES = frozenset({"variables", "inputs", "jobs", "auto"})

SENSITIVE_MASK = "****"


def parse_path_list(value: str) -> list[str]:
    """Split comma-separated YAML paths (whitespace trimmed)."""
    return [part.strip() for part in value.split(",") if part.strip()]


def is_legacy_render_mode(render: str) -> bool:
    return "." not in render and render.lower() in LEGACY_RENDER_MODES


def normalize_legacy_render(render: str) -> str:
    mode = (render or "auto").lower()
    return mode if mode in LEGACY_RENDER_MODES else "auto"


def _match_dict_key(mapping: dict, key: str, *, job_names: bool) -> str | None:
    if key in mapping:
        return key
    if not job_names:
        return None
    folded = key.casefold()
    for candidate in mapping:
        if candidate.casefold() == folded:
            return candidate
    return None


def resolve_yaml_path(root: Any, path: str) -> Any | None:
    """Walk a dot-separated path; job names match case-insensitively at the pipeline root."""
    if root is None or not path or not str(path).strip():
        return None
    segments = [s for s in str(path).strip().split(".") if s]
    node: Any = root
    for index, segment in enumerate(segments):
        if not isinstance(node, dict):
            return None
        job_names = index == 0 and isinstance(root, dict)
        matched = _match_dict_key(node, segment, job_names=job_names)
        if matched is None:
            return None
        node = node[matched]
    return node


def value_path_for_variable(prefix: str, key: str, raw_value: Any) -> str:
    base = f"{prefix}.{key}" if prefix else key
    if isinstance(raw_value, dict) and "value" in raw_value:
        return f"{base}.value"
    return base


def should_mask_value(canonical_value_path: str, sensitive_paths: list[str]) -> bool:
    if not sensitive_paths:
        return False
    target = canonical_value_path.strip()
    for sensitive in sensitive_paths:
        s = sensitive.strip()
        if not s:
            continue
        if target == s or target.casefold() == s.casefold():
            return True
    return False
