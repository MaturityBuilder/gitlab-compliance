"""Build a supply-chain inventory from a GitLab CI pipeline."""

from __future__ import annotations

import hashlib
import os
from typing import Any
from urllib.parse import quote, urlparse

from src.compliance.image_versions import (
    declared_image_tag,
    parse_container_image_ref,
    resolve_declared_image_digest,
)
from src.compliance.include_fetch import (
    FetchedInclude,
    default_gitlab_url,
    fetch_include_content,
    resolve_project_commit_sha,
)
from src.compliance.include_versions import resolve_include_project_path
from src.compliance.release_cache import ReleaseMetadataCache
from src.modules.pipeline_data import (
    _resolve_generated_artifact_path,
    _resolve_local_include_path,
    collect_pipeline_data,
)

_PACKAGE_PURL_TYPES = {
    "pypi": "pypi",
    "npm": "npm",
    "apk": "apk",
    "deb": "deb",
    "rpm": "rpm",
    "golang": "golang",
}


def _quote_purl_name(name: str) -> str:
    return quote(str(name or "").strip(), safe="/")


def build_purl(
    package_type: str,
    name: str,
    version: str = "",
    qualifiers: dict[str, str] | None = None,
) -> str:
    """Build a package URL, omitting empty versions and qualifiers."""
    version_text = str(version or "").strip()
    version_part = ""
    if version_text and version_text != "n/a":
        version_part = "@" + quote(version_text, safe="")
    query = ""
    if qualifiers:
        parts = []
        for key, value in qualifiers.items():
            if value is None or str(value) == "":
                continue
            parts.append(f"{quote(str(key), safe='')}={quote(str(value), safe='')}")
        if parts:
            query = "?" + "&".join(parts)
    return f"pkg:{package_type}/{_quote_purl_name(name)}{version_part}{query}"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_qualifier(file_value: Any) -> str:
    if isinstance(file_value, list):
        return ",".join(str(item) for item in file_value if item)
    return str(file_value or "")


def _occurrence(location: str, line: int, context: str) -> dict[str, Any]:
    record: dict[str, Any] = {"location": location or "", "context": context or ""}
    if line:
        record["line"] = int(line)
    return record


def _add_component(components: dict[str, dict], component: dict) -> None:
    purl = component.get("purl") or ""
    if not purl:
        return
    existing = components.get(purl)
    if existing is None:
        components[purl] = component
        return
    seen = {
        (item.get("location"), item.get("line", 0), item.get("context"))
        for item in existing["occurrences"]
    }
    for item in component.get("occurrences") or []:
        key = (item.get("location"), item.get("line", 0), item.get("context"))
        if key not in seen:
            existing["occurrences"].append(item)
            seen.add(key)
    if not existing.get("hashes") and component.get("hashes"):
        existing["hashes"] = list(component["hashes"])
    for key, value in (component.get("properties") or {}).items():
        if value and not existing["properties"].get(key):
            existing["properties"][key] = value


def _container_component(
    image_ref: str,
    *,
    image_source: str,
    parent_job: str,
    source_file: str,
    line: int,
    resolved_digest: str = "",
) -> dict | None:
    parsed = parse_container_image_ref(image_ref)
    if not parsed or not parsed.get("repository"):
        return None
    tag = declared_image_tag(image_ref)
    digest = str(resolved_digest or parsed.get("digest") or "")
    purl_version = f"sha256:{digest}" if digest else tag
    qualifiers = {"repository_url": parsed.get("registry") or ""}
    if tag:
        qualifiers["tag"] = tag
    properties = {
        "gitlab-compliance:component-kind": "container",
        "gitlab-compliance:image-source": image_source,
        "gitlab-compliance:declared-version": tag,
    }
    if digest:
        properties["gitlab-compliance:resolved-digest"] = digest
    return {
        "type": "container",
        "name": parsed["repository"].rsplit("/", 1)[-1],
        "version": tag or (f"sha256:{digest}" if digest else ""),
        "purl": build_purl(
            "oci",
            parsed["repository"],
            purl_version,
            qualifiers,
        ),
        "hashes": [digest] if digest else [],
        "properties": properties,
        "external_references": [],
        "occurrences": [_occurrence(source_file, line, parent_job or image_source)],
    }


def _include_name(include: dict) -> str:
    project = str(include.get("project") or include.get("artifact") or "")
    include_type = str(include.get("include_type") or "")
    if include_type == "remote":
        path = urlparse(project).path.rstrip("/")
        return path.rsplit("/", 1)[-1] or "remote-include"
    if include_type == "template":
        return project or "gitlab-template"
    leaf = project.rstrip("/").rsplit("/", 1)[-1]
    return leaf or project or "include"


def _include_component(include: dict, pipeline_file: str) -> dict | None:
    include_type = str(include.get("include_type") or "")
    project = str(include.get("project") or "")
    version = str(include.get("version") or "")
    if version == "n/a":
        version = ""
    source_file = str(include.get("source_file") or pipeline_file)
    line = int(include.get("line") or 0)
    content_hash = str(include.get("content_sha256") or "")
    resolved_commit = str(include.get("resolved_commit") or "")
    properties = {
        "gitlab-compliance:component-kind": "include",
        "gitlab-compliance:include-type": include_type,
        "gitlab-compliance:declared-version": version,
    }
    if resolved_commit:
        properties["gitlab-compliance:resolved-commit"] = resolved_commit
    external_references: list[dict[str, str]] = []
    component_type = "library"
    purl = ""

    if include_type in {"project", "component"}:
        qualifiers = {}
        file_value = _file_qualifier(include.get("file"))
        if include_type == "project" and file_value:
            qualifiers["file"] = file_value
        if include_type == "component":
            qualifiers["component"] = _include_name(include)
        purl = build_purl("gitlab", project or "unknown", version, qualifiers)
    elif include_type == "remote":
        component_type = "file"
        external_references.append({"type": "distribution", "url": project})
        purl = build_purl("generic", _include_name(include), version)
    elif include_type == "template":
        component_type = "file"
        purl = build_purl("generic", f"gitlab-template/{project or 'template'}")
    elif include_type == "local":
        component_type = "file"
        purl_version = content_hash or version
        purl = build_purl("generic", project or "local-include", purl_version)
    elif include_type == "artifact":
        component_type = "file"
        artifact = str(include.get("artifact") or project)
        purl = build_purl("generic", artifact or "generated-pipeline", content_hash)
        properties["gitlab-compliance:include-type"] = "artifact"
    else:
        return None

    return {
        "type": component_type,
        "name": _include_name(include),
        "version": version,
        "purl": purl,
        "hashes": [content_hash] if content_hash else [],
        "properties": properties,
        "external_references": external_references,
        "occurrences": [_occurrence(source_file, line, include_type)],
    }


def _package_component(package: dict) -> dict | None:
    ecosystem = str(package.get("ecosystem") or "")
    if ecosystem == "docker":
        return _container_component(
            str(package.get("name") or ""),
            image_source="script",
            parent_job=str(package.get("parent_job") or ""),
            source_file=str(package.get("source_file") or ""),
            line=int(package.get("line") or 0),
            resolved_digest=str(package.get("resolved_digest") or ""),
        )
    purl_type = _PACKAGE_PURL_TYPES.get(ecosystem)
    if not purl_type:
        return None
    name = str(package.get("name") or "")
    version = str(package.get("version") or "")
    pinned = bool(package.get("pinned"))
    return {
        "type": "library",
        "name": name,
        "version": version,
        "purl": build_purl(purl_type, name, version),
        "hashes": [],
        "properties": {
            "gitlab-compliance:component-kind": "package",
            "gitlab-compliance:ecosystem": ecosystem,
            "gitlab-compliance:declared-version": version,
            "gitlab-compliance:pinned": "true" if pinned else "false",
        },
        "external_references": [],
        "occurrences": [
            _occurrence(
                str(package.get("source_file") or ""),
                int(package.get("line") or 0),
                str(package.get("parent_job") or ""),
            )
        ],
    }


def components_from_pipeline(data: dict, pipeline_file: str) -> list[dict]:
    """Dedupe includes, images, and script packages into SBOM components."""
    components: dict[str, dict] = {}
    for include in data.get("includes") or []:
        component = _include_component(include, pipeline_file)
        if component:
            _add_component(components, component)
    for image in data.get("container_images") or []:
        component = _container_component(
            str(image.get("image") or image.get("project") or ""),
            image_source=str(image.get("image_source") or "job"),
            parent_job=str(image.get("parent_job") or ""),
            source_file=str(image.get("source_file") or ""),
            line=int(image.get("line") or 0),
            resolved_digest=str(image.get("resolved_digest") or ""),
        )
        if component:
            _add_component(components, component)
    for package in data.get("script_packages") or []:
        component = _package_component(package)
        if component:
            _add_component(components, component)
    for child in data.get("dynamic_child_pipelines") or []:
        if str(child.get("include_type") or "") != "artifact":
            continue
        component = _include_component(
            {
                "include_type": "artifact",
                "project": child.get("artifact") or "",
                "artifact": child.get("artifact") or "",
                "version": "",
                "source_file": child.get("source_file") or "",
                "line": child.get("line") or 0,
                "content_sha256": child.get("content_sha256") or "",
            },
            pipeline_file,
        )
        if component:
            _add_component(components, component)
    return [components[key] for key in sorted(components)]


def _resolve_include(
    include: dict,
    *,
    pipeline_file: str,
    gitlab_url: str | None,
    token: str | None,
) -> dict:
    include_type = str(include.get("include_type") or "")
    source_file = str(include.get("source_file") or pipeline_file)
    if include_type == "local":
        resolved = _resolve_local_include_path(
            source_file, str(include.get("project") or "")
        )
        if resolved and os.path.isfile(resolved):
            try:
                include["content_sha256"] = _sha256_file(resolved)
            except OSError:
                include["content_sha256"] = ""
        return include

    if include_type == "remote":
        fetched = fetch_include_content(
            include,
            gitlab_url=default_gitlab_url(gitlab_url),
            token=token,
        )
        if isinstance(fetched, FetchedInclude):
            include["content_sha256"] = _sha256_text(fetched.yaml_text)
        return include

    if include_type == "project" and token:
        project_path = resolve_include_project_path(
            "project", str(include.get("project") or "")
        )
        ref = str(include.get("version") or "")
        if ref in {"", "n/a"}:
            ref = "HEAD"
        if project_path:
            include["resolved_commit"] = resolve_project_commit_sha(
                project_path,
                ref,
                gitlab_url=default_gitlab_url(gitlab_url),
                token=token,
            )
        fetched = fetch_include_content(
            include,
            gitlab_url=default_gitlab_url(gitlab_url),
            token=token,
        )
        if isinstance(fetched, FetchedInclude):
            include["content_sha256"] = _sha256_text(fetched.yaml_text)
    return include


def _resolve_artifact(child: dict, pipeline_file: str) -> dict:
    if str(child.get("include_type") or "") != "artifact":
        return child
    source_file = str(child.get("source_file") or pipeline_file)
    resolved, _reason = _resolve_generated_artifact_path(
        source_file, str(child.get("artifact") or "")
    )
    if resolved and os.path.isfile(resolved):
        try:
            child["content_sha256"] = _sha256_file(resolved)
        except OSError:
            child["content_sha256"] = ""
    return child


def resolve_inventory(
    data: dict,
    *,
    pipeline_file: str,
    gitlab_url: str | None,
    token: str | None,
) -> dict:
    """Attach digests, commit SHAs, and file hashes for the pins as written."""
    resolved = dict(data)
    cache = ReleaseMetadataCache()
    images = []
    for image in data.get("container_images") or []:
        item = dict(image)
        item["resolved_digest"] = resolve_declared_image_digest(
            str(item.get("image") or ""),
            gitlab_url=gitlab_url,
            token=token,
            cache=cache,
        )
        images.append(item)
    resolved["container_images"] = images

    includes = []
    for include in data.get("includes") or []:
        includes.append(
            _resolve_include(
                dict(include),
                pipeline_file=pipeline_file,
                gitlab_url=gitlab_url,
                token=token,
            )
        )
    resolved["includes"] = includes

    packages = []
    for package in data.get("script_packages") or []:
        item = dict(package)
        if item.get("ecosystem") == "docker":
            item["resolved_digest"] = resolve_declared_image_digest(
                str(item.get("name") or ""),
                gitlab_url=gitlab_url,
                token=token,
                cache=cache,
            )
        packages.append(item)
    resolved["script_packages"] = packages

    children = []
    for child in data.get("dynamic_child_pipelines") or []:
        children.append(_resolve_artifact(dict(child), pipeline_file))
    resolved["dynamic_child_pipelines"] = children
    return resolved


def load_pipeline_inventory(
    pipeline_file: str,
    *,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    resolve_external_includes: bool | None = None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    resolve: bool = False,
) -> dict:
    """Load pipeline data and optionally resolve immutable pin identities."""
    data = collect_pipeline_data(
        pipeline_file,
        detailed=True,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        include_scripts=True,
        resolve_job_composition=True,
        resolve_external_includes=resolve_external_includes,
        resolve_generated=resolve_generated,
        generated_configs=generated_configs,
        gitlab_url=gitlab_url,
        token=token,
    )
    if not resolve:
        return data
    return resolve_inventory(
        data,
        pipeline_file=pipeline_file,
        gitlab_url=gitlab_url,
        token=token,
    )
