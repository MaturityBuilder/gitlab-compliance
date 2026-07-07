"""Include version validation and GitLab release metadata for compliance checks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import semver

from src.compliance.release_cache import ReleaseMetadataCache
from src.modules.release import parse_gitlab_date


def is_valid_semver_version(version: str) -> bool:
    if not version or not str(version).strip():
        return False
    try:
        return semver.Version.is_valid(str(version).strip())
    except Exception:
        return False


def resolve_include_project_path(include_type: str, project: str) -> str | None:
    if include_type not in {"project", "component"}:
        return None

    path = str(project or "").strip()
    if not path:
        return None

    if path.startswith("http://") or path.startswith("https://"):
        path = urlparse(path).path.lstrip("/")
    elif "/" in path and "." in path.split("/", 1)[0]:
        path = "/".join(path.split("/")[1:])

    if path.endswith(".git"):
        path = path[:-4]

    return path or None


def days_between(start: datetime, end: datetime) -> int:
    """Whole days from start to end (end may be before start)."""
    start_utc = start.astimezone(timezone.utc)
    end_utc = end.astimezone(timezone.utc)
    return (end_utc.date() - start_utc.date()).days


def compute_release_lag_days(
    pinned_date: datetime | None, latest_date: datetime | None
) -> int | None:
    if pinned_date is None or latest_date is None:
        return None
    return days_between(pinned_date, latest_date)


def compute_latest_release_age_days(
    latest_date: datetime | None, *, now: datetime | None = None
) -> int | None:
    if latest_date is None:
        return None
    reference = now or datetime.now(timezone.utc)
    return days_between(latest_date, reference)


def _tag_committed_date(tag: Any) -> datetime | None:
    commit = getattr(tag, "commit", None) or {}
    if isinstance(commit, dict):
        committed_date = commit.get("committed_date")
    else:
        committed_date = getattr(commit, "committed_date", None)
    if not committed_date:
        return None
    try:
        return parse_gitlab_date(str(committed_date))
    except ValueError:
        return None


def fetch_semver_tag_dates(
    gl: Any,
    project_path: str,
    *,
    gitlab_url: str | None = None,
    cache: ReleaseMetadataCache | None = None,
) -> dict[str, datetime]:
    """Map semver tag names to commit dates from a single tags.list call."""
    if cache is not None and gitlab_url:
        cached = cache.get_gitlab_tag_dates(gitlab_url, project_path)
        if cached is not None:
            return cached

    project = gl.projects.get(project_path)
    tag_dates: dict[str, datetime] = {}
    for tag in project.tags.list(all=True):
        if not is_valid_semver_version(tag.name):
            continue
        committed_date = _tag_committed_date(tag)
        if committed_date is not None:
            tag_dates[tag.name] = committed_date

    if cache is not None and gitlab_url:
        cache.set_gitlab_tag_dates(gitlab_url, project_path, tag_dates)
    return tag_dates


def _semver_tags_descending(tag_names: list[str]) -> list[str]:
    valid = [name for name in tag_names if is_valid_semver_version(name)]
    return sorted(valid, key=lambda value: semver.Version.parse(value), reverse=True)


def compute_version_tag_rank(version: str, tags_desc: list[str]) -> int | None:
    try:
        return tags_desc.index(version) + 1
    except ValueError:
        return None


def version_within_latest_tags(version: str, tags_desc: list[str], count: int) -> bool:
    rank = compute_version_tag_rank(version, tags_desc)
    if rank is None:
        return False
    return rank <= count


def _latest_semver_tag(tag_names: list[str]) -> str | None:
    valid = [name for name in tag_names if is_valid_semver_version(name)]
    if not valid:
        return None
    return max(valid, key=lambda value: semver.Version.parse(value))


def fetch_latest_semver_version(gl: Any, project_path: str) -> str | None:
    tag_dates = fetch_semver_tag_dates(gl, project_path)
    return _latest_semver_tag(list(tag_dates.keys()))


def include_update_available(current_version: str, latest_version: str) -> bool:
    if not latest_version:
        return False
    current = str(current_version or "").strip()
    if not is_valid_semver_version(current):
        return is_valid_semver_version(latest_version)
    if not is_valid_semver_version(latest_version):
        return False
    return semver.Version.parse(latest_version) > semver.Version.parse(current_version)


def enrich_include_release_metadata(
    include: dict,
    *,
    gitlab_url: str | None,
    token: str,
    gl: Any | None = None,
    cache: ReleaseMetadataCache | None = None,
) -> dict:
    enriched = dict(include)
    include_type = enriched.get("include_type", "")
    version = str(enriched.get("version", "")).strip()
    enriched["valid_version"] = is_valid_semver_version(version)
    enriched["latest_version"] = ""
    enriched["update_available"] = False
    enriched["release_metadata_resolved"] = False
    enriched["version_released_at"] = ""
    enriched["latest_version_released_at"] = ""
    enriched["latest_release_age_days"] = None
    enriched["release_lag_days"] = None
    enriched["version_tag_rank"] = None
    enriched["semver_tag_count"] = 0

    project_path = resolve_include_project_path(include_type, enriched.get("project", ""))
    if not project_path:
        return enriched

    gitlab_url = (
        gitlab_url
        or os.getenv("CI_SERVER_URL")
        or os.getenv("GITLAB_URL")
        or "https://gitlab.com"
    )

    try:
        if gl is None:
            import gitlab

            gl = gitlab.Gitlab(gitlab_url, private_token=token)
            gl.auth()
        tag_dates = fetch_semver_tag_dates(
            gl, project_path, gitlab_url=gitlab_url, cache=cache
        )
    except Exception:
        return enriched

    latest_version = _latest_semver_tag(list(tag_dates.keys()))
    if not latest_version:
        return enriched

    tags_desc = _semver_tags_descending(list(tag_dates.keys()))
    pinned_date = tag_dates.get(version) if enriched["valid_version"] else None
    latest_date = tag_dates.get(latest_version)

    enriched["latest_version"] = latest_version
    enriched["update_available"] = include_update_available(version, latest_version)
    enriched["release_metadata_resolved"] = True
    enriched["semver_tag_count"] = len(tags_desc)
    if enriched["valid_version"]:
        enriched["version_tag_rank"] = compute_version_tag_rank(version, tags_desc)

    if pinned_date is not None:
        enriched["version_released_at"] = pinned_date.isoformat()
    if latest_date is not None:
        enriched["latest_version_released_at"] = latest_date.isoformat()
        enriched["latest_release_age_days"] = compute_latest_release_age_days(latest_date)

    if enriched["update_available"] and pinned_date is not None and latest_date is not None:
        enriched["release_lag_days"] = compute_release_lag_days(pinned_date, latest_date)

    return enriched


def enrich_includes_with_releases(
    includes: list[dict],
    *,
    gitlab_url: str | None,
    token: str,
    gl: Any | None = None,
    cache: ReleaseMetadataCache | None = None,
) -> list[dict]:
    return [
        enrich_include_release_metadata(
            include,
            gitlab_url=gitlab_url,
            token=token,
            gl=gl,
            cache=cache,
        )
        for include in includes
    ]
