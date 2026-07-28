"""Fetch GitLab CI YAML from remote and project include entries."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import requests

from src.compliance.include_versions import resolve_include_project_path
from src.modules.common import load_yml_documents

GITLAB_TEMPLATE_BASE = (
    "https://gitlab.com/gitlab-org/gitlab/-/raw/master/lib/gitlab/ci/templates"
)


@dataclass(frozen=True)
class FetchedInclude:
    """YAML content retrieved from an external include."""

    config_label: str
    yaml_text: str


@dataclass(frozen=True)
class IncludeFetchFailure:
    """Reason an include could not be fetched."""

    reason: str
    detail: str = ""


@dataclass
class IncludeFetchCache:
    """In-memory cache for fetched include YAML."""

    entries: dict[str, FetchedInclude | IncludeFetchFailure] = field(
        default_factory=dict
    )


def _cache_key(include_type: str, *parts: str) -> str:
    return f"{include_type}:" + ":".join(parts)


def _gitlab_client(gitlab_url: str, token: str):
    import gitlab

    client = gitlab.Gitlab(gitlab_url, private_token=token)
    client.auth()
    return client


def _normalize_project_files(file_value: Any) -> list[str]:
    if file_value is None or file_value == "":
        return [".gitlab-ci.yml"]
    if isinstance(file_value, str):
        return [file_value]
    if isinstance(file_value, list):
        return [str(item) for item in file_value if item]
    return [str(file_value)]


def _fetch_remote(url: str, token: str | None) -> FetchedInclude | IncludeFetchFailure:
    headers: dict[str, str] = {}
    if token:
        headers["PRIVATE-TOKEN"] = token
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        return IncludeFetchFailure(reason="fetch_failed", detail=str(exc))
    text = response.text
    if not text.strip():
        return IncludeFetchFailure(reason="fetch_failed", detail="empty response")
    try:
        load_yml_documents(text)
    except Exception as exc:
        return IncludeFetchFailure(reason="fetch_failed", detail=f"invalid YAML: {exc}")
    return FetchedInclude(config_label=url, yaml_text=text)


def _fetch_project_files(
    *,
    project_path: str,
    ref: str,
    files: list[str],
    gitlab_url: str,
    token: str,
) -> FetchedInclude | IncludeFetchFailure:
    try:
        gl = _gitlab_client(gitlab_url, token)
        project = gl.projects.get(project_path)
    except Exception as exc:
        return IncludeFetchFailure(reason="fetch_failed", detail=str(exc))

    documents: list[dict] = []
    label_parts: list[str] = []
    for file_path in files:
        try:
            raw = project.files.raw(file_path=file_path, ref=ref or "main")
        except Exception as exc:
            return IncludeFetchFailure(
                reason="fetch_failed",
                detail=f"{file_path}@{ref or 'main'}: {exc}",
            )
        text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        try:
            parsed_docs = load_yml_documents(text)
        except Exception as exc:
            return IncludeFetchFailure(
                reason="fetch_failed",
                detail=f"{file_path}: invalid YAML: {exc}",
            )
        documents.extend(doc for doc in parsed_docs if isinstance(doc, dict))
        label_parts.append(file_path)

    if not documents:
        return IncludeFetchFailure(reason="fetch_failed", detail="no YAML documents")

    import yaml

    merged = yaml.safe_dump_all(documents, sort_keys=False)
    label = f"project:{project_path}@{ref or 'main'}:" + ",".join(label_parts)
    return FetchedInclude(config_label=label, yaml_text=merged)


def _fetch_template(template_name: str) -> FetchedInclude | IncludeFetchFailure:
    name = str(template_name).strip()
    if not name:
        return IncludeFetchFailure(
            reason="unsupported_type", detail="empty template name"
        )
    url = f"{GITLAB_TEMPLATE_BASE}/{name}"
    return _fetch_remote(url, token=None)


def fetch_include_content(
    parsed: dict[str, Any],
    *,
    gitlab_url: str,
    token: str | None,
    cache: IncludeFetchCache | None = None,
    allow_template: bool = False,
) -> FetchedInclude | IncludeFetchFailure:
    """Fetch YAML for a parsed include entry (remote or project)."""
    include_type = parsed.get("include_type", "")
    cache = cache or IncludeFetchCache()

    if include_type == "remote":
        url = str(parsed.get("project", "")).strip()
        key = _cache_key("remote", url)
        if key in cache.entries:
            return cache.entries[key]
        result = _fetch_remote(url, token)
        cache.entries[key] = result
        return result

    if include_type == "project":
        if not token:
            return IncludeFetchFailure(reason="no_token")
        project_path = resolve_include_project_path(
            "project", str(parsed.get("project", ""))
        )
        if not project_path:
            return IncludeFetchFailure(
                reason="fetch_failed", detail="could not resolve project path"
            )
        ref = str(parsed.get("version", "") or parsed.get("ref", "") or "main")
        files = _normalize_project_files(parsed.get("file"))
        key = _cache_key("project", project_path, ref, *files)
        if key in cache.entries:
            return cache.entries[key]
        result = _fetch_project_files(
            project_path=project_path,
            ref=ref,
            files=files,
            gitlab_url=gitlab_url,
            token=token,
        )
        cache.entries[key] = result
        return result

    if include_type == "template" and allow_template:
        template_name = str(parsed.get("project", "")).strip()
        key = _cache_key("template", template_name)
        if key in cache.entries:
            return cache.entries[key]
        result = _fetch_template(template_name)
        cache.entries[key] = result
        return result

    if include_type in {"component", "template"}:
        return IncludeFetchFailure(reason="unsupported_type")

    return IncludeFetchFailure(reason="unsupported_type", detail=include_type)


def include_reference_label(parsed: dict[str, Any]) -> str:
    """Human-readable label for an include entry."""
    include_type = parsed.get("include_type", "unknown")
    if include_type == "local":
        return str(parsed.get("project", ""))
    if include_type == "remote":
        return str(parsed.get("project", ""))
    if include_type == "project":
        file_part = parsed.get("file") or ".gitlab-ci.yml"
        ref = parsed.get("version") or "main"
        return f"{parsed.get('project', '')} ({file_part} @ {ref})"
    if include_type == "component":
        return f"{parsed.get('project', '')}@{parsed.get('version', '')}"
    if include_type == "template":
        return str(parsed.get("project", ""))
    return str(parsed.get("project", ""))


def default_gitlab_url(gitlab_url: str | None = None) -> str:
    if gitlab_url:
        return gitlab_url.rstrip("/")
    for env_key in ("CI_SERVER_URL", "GITLAB_URL"):
        value = os.getenv(env_key)
        if value:
            return value.rstrip("/")
    return "https://gitlab.com"


def is_public_gitlab_host(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc in {"gitlab.com", "www.gitlab.com"}
