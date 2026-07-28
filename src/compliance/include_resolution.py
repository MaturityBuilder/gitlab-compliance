"""Include resolution reporting for compliance and shell-check runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.compliance.include_fetch import include_reference_label

REASON_MESSAGES = {
    "no_token": "missing authentication",  # nosec B105 - user-facing reason label
    "fetch_failed": "fetch failed",
    "unsupported_type": "unsupported include type",
    "depth_exceeded": "max include depth exceeded",
    "include_nested_disabled": "nested includes disabled",
    "external_resolution_disabled": "external include resolution disabled",
    "path_rejected": "local include path rejected",
    "not_found": "include file not found",
}


@dataclass(frozen=True)
class UnresolvedInclude:
    """An include entry that was not merged into the pipeline stash."""

    include_type: str
    reference: str
    reason: str
    source_file: str = ""
    line: int = 0
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "include_type": self.include_type,
            "reference": self.reference,
            "reason": self.reason,
            "source_file": self.source_file,
            "line": self.line,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> UnresolvedInclude:
        return cls(
            include_type=str(payload.get("include_type", "")),
            reference=str(payload.get("reference", "")),
            reason=str(payload.get("reason", "")),
            source_file=str(payload.get("source_file", "")),
            line=int(payload.get("line") or 0),
            detail=str(payload.get("detail", "")),
        )


@dataclass
class IncludeResolutionReport:
    """Aggregated include coverage information for a pipeline load."""

    unresolved: list[UnresolvedInclude] = field(default_factory=list)

    def extend(self, items: list[UnresolvedInclude | dict[str, Any]]) -> None:
        for item in items:
            if isinstance(item, UnresolvedInclude):
                self.unresolved.append(item)
            else:
                self.unresolved.append(UnresolvedInclude.from_dict(item))

    def to_dicts(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.unresolved]

    def has_gaps(self) -> bool:
        return bool(self.unresolved)


def record_unresolved(
    bucket: list[UnresolvedInclude],
    parsed: dict[str, Any],
    *,
    reason: str,
    detail: str = "",
) -> None:
    bucket.append(
        UnresolvedInclude(
            include_type=str(parsed.get("include_type", "")),
            reference=include_reference_label(parsed),
            reason=reason,
            source_file=str(parsed.get("source_file", "")),
            line=int(parsed.get("line") or 0),
            detail=detail,
        )
    )


def format_include_warning(report: IncludeResolutionReport) -> str:
    """Format unresolved includes for console warnings."""
    if not report.unresolved:
        return ""

    lines = [
        "Some include entries were not resolved; scripts from those files were "
        + "not validated. Pass --token (or set GITLAB_TOKEN) and enable external "
        + "include resolution to fetch project and remote includes.",
        "",
    ]
    for item in report.unresolved:
        reason = REASON_MESSAGES.get(item.reason, item.reason)
        detail = f" ({item.detail})" if item.detail else ""
        location = ""
        if item.source_file:
            location = f" in {item.source_file}"
            if item.line:
                location += f":{item.line}"
        lines.append(
            f"- [{item.include_type}] {item.reference}{location}: {reason}{detail}"
        )
    return "\n".join(lines)
