"""Filter and group pipeline documentation output for ``generate``."""

from __future__ import annotations

import sys
from typing import Any

import src.modules.common as common

KNOWN_SECTIONS = frozenset(
    {"inputs", "variables", "includes", "workflow", "jobs", "container_images"}
)

UNSET_GROUP_KEY = "(unset)"


def parse_exclude(exclude: str | None) -> tuple[set[str], set[str]]:
    """Split a comma-separated exclude list into section and attribute sets."""
    if not exclude or not exclude.strip():
        return set(), set()

    sections: set[str] = set()
    attributes: set[str] = set()
    for token in exclude.split(","):
        name = token.strip().lower()
        if not name:
            continue
        if name in KNOWN_SECTIONS:
            sections.add(name)
        else:
            attributes.add(name)
    return sections, attributes


def validate_exclude_sections(exclude_sections: set[str]) -> None:
    """Raise ValueError if any section name is not recognised."""
    unknown = exclude_sections - KNOWN_SECTIONS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(
            f"Unknown section(s) in --exclude: {names}. "
            f"Valid sections: {', '.join(sorted(KNOWN_SECTIONS))}"
        )


def warn_group_by_excluded(group_by: str | None, exclude_attributes: set[str]) -> None:
    """Warn when group-by attribute is also excluded from job detail."""
    if group_by and group_by.lower() in {a.lower() for a in exclude_attributes}:
        print(
            f"Warning: --group-by '{group_by}' is also in --exclude; "
            "grouping still applies but the attribute is hidden in job detail.",
            file=sys.stderr,
        )


def _job_attribute_value(job: dict, attribute: str) -> Any:
    """Return a job's top-level attribute value, including nested ``variables``."""
    for item in job.get("attributes", []):
        if item.get("key") == attribute:
            return item.get("value")
    for item in job.get("nested", []):
        if item.get("attribute") == attribute:
            return item.get("value")
    if attribute == "rules":
        return job.get("rules") or None
    return None


def filter_job(job: dict, exclude_attributes: set[str]) -> dict:
    """Return a copy of *job* with excluded attributes removed."""
    if not exclude_attributes:
        return job

    lowered = {name.lower() for name in exclude_attributes}
    filtered = dict(job)
    filtered["attributes"] = [
        item
        for item in job.get("attributes", [])
        if item.get("key", "").lower() not in lowered
    ]
    filtered["nested"] = [
        item
        for item in job.get("nested", [])
        if item.get("attribute", "").lower() not in lowered
    ]
    if "rules" in lowered:
        filtered["rules"] = []
    return filtered


def group_jobs(jobs: list[dict], group_by: str | None) -> list[dict]:
    """Group jobs by a top-level attribute value.

    Returns a list of ``{"group_key": str, "jobs": list[dict]}`` blocks.
    When *group_by* is None, returns a single block with all jobs.
    """
    if not group_by:
        return [{"group_key": "", "jobs": jobs}]

    buckets: dict[str, list[dict]] = {}
    order: list[str] = []

    for job in jobs:
        raw = _job_attribute_value(job, group_by)
        if raw is None or raw == "":
            key = UNSET_GROUP_KEY
        elif isinstance(raw, (dict, list)):
            key = common.format_value(raw)
        else:
            key = str(raw)

        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(job)

    return [{"group_key": key, "jobs": buckets[key]} for key in order]


def apply_output_filters(
    data: dict,
    exclude_sections: set[str] | None = None,
    exclude_attributes: set[str] | None = None,
    group_by: str | None = None,
) -> dict:
    """Apply section/attribute filters and build ``jobs_grouped`` on *data*."""
    sections = exclude_sections or set()
    attributes = exclude_attributes or set()

    filtered = dict(data)
    filtered["exclude_sections"] = sections
    filtered["exclude_attributes"] = attributes
    filtered["group_by"] = group_by

    if "inputs" in sections:
        filtered["inputs"] = []
    if "variables" in sections:
        filtered["variables"] = []
    if "includes" in sections:
        filtered["includes"] = []
    if "workflow" in sections:
        filtered["workflow_rules"] = []
    if "jobs" in sections:
        filtered["jobs"] = []
        filtered["container_images"] = []
    elif "container_images" in sections:
        filtered["container_images"] = []
    else:
        jobs = [filter_job(job, attributes) for job in filtered.get("jobs", [])]
        filtered["jobs"] = jobs
        if "container_images" not in sections:
            # container_images may already be populated; leave as-is unless excluded
            pass

    if "jobs" not in sections:
        filtered["jobs_grouped"] = group_jobs(filtered.get("jobs", []), group_by)
    else:
        filtered["jobs_grouped"] = []

    return filtered
