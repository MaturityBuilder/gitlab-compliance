"""GitLab CI ``!reference`` tag support for YAML loading."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UnresolvedReference:
    """Marker left by EnvLoader until a job registry can resolve the path."""

    path: tuple[Any, ...]

    def __str__(self) -> str:
        return f"!reference {list(self.path)}"


def construct_reference(loader, node):
    """PyYAML constructor for GitLab ``!reference`` tags."""
    if loader is None:
        raw = getattr(node, "value", None)
        if isinstance(raw, list):
            return UnresolvedReference(path=tuple(raw))
        return UnresolvedReference(path=(raw,))
    if hasattr(node, "value") and isinstance(node.value, list):
        constructed = loader.construct_sequence(node)
    else:
        constructed = loader.construct_object(node)
    if isinstance(constructed, list):
        return UnresolvedReference(path=tuple(constructed))
    return UnresolvedReference(path=(constructed,))


def resolve_reference_value(
    reference: UnresolvedReference, job_registry: dict[str, dict]
) -> Any:
    """Resolve ``!reference [job, key, ...]`` against a job registry.

    Returns the referenced value, or the original ``UnresolvedReference`` when
    the path cannot be resolved.
    """
    if not reference.path:
        return reference
    job_name = reference.path[0]
    if job_name not in job_registry:
        return reference
    current: Any = job_registry[job_name].get("config", {})
    for part in reference.path[1:]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return reference
    return current
