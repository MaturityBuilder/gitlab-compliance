"""Collect structured pipeline documentation from GitLab CI YAML."""

from __future__ import annotations

import os
import re
import tempfile
from typing import Any

import src.modules.common as common
from src.compliance.include_fetch import (
    ExternalIncludeContext,
    IncludeFetchCache,
    IncludeFetchFailure,
    context_for_fetched,
    default_gitlab_url,
    fetch_include_content,
    resolve_nested_local_from_context,
)
from src.compliance.include_resolution import UnresolvedInclude, record_unresolved
from src.compliance.include_versions import is_valid_semver_version
from src.modules.job_composition import compose_job_scripts, register_job_entry
from src.modules.output_filters import apply_output_filters

JOB_EXCLUDE_KEYWORDS = [
    "default",
    "include",
    "stages",
    "variables",
    "workflow",
    "image",
    "spec",
]

JOB_SKIP_ATTRIBUTES = {"before_script", "script", "after_script", "artifacts"}
SCRIPT_ATTRIBUTE_KEYS = frozenset({"before_script", "script", "after_script"})

_REMOTE_VERSION_RE = re.compile(
    r"(?:^|/)(v?\d+\.\d+\.\d+(?:[-+][\w.-]+)?|[0-9a-f]{40})(?:/|$)",
    re.IGNORECASE,
)


def _normalize_include(entry: Any) -> dict:
    if isinstance(entry, str):
        return {"local": entry}
    return entry


def _iter_include_entries(include_value: Any) -> list[Any]:
    """Normalize GitLab ``include`` values to a list of include specs."""
    if include_value is None:
        return []
    if isinstance(include_value, str):
        return [include_value]
    if isinstance(include_value, dict):
        return [include_value]
    if isinstance(include_value, list):
        return include_value
    return [include_value]


def _include_valid_version(version: str, file: str, include: str) -> bool:
    return is_valid_semver_version(version)


def _parse_remote_url_version(url: str) -> str:
    match = _REMOTE_VERSION_RE.search(str(url))
    if not match:
        return ""
    return match.group(1).lstrip("vV")


def _parse_image_reference(image_value: Any) -> str:
    if isinstance(image_value, dict):
        return str(image_value.get("name", "")).strip()
    return str(image_value or "").strip()


def _parse_service_image(service: Any) -> str:
    if isinstance(service, str):
        return service.strip()
    if isinstance(service, dict):
        return str(service.get("name", "")).strip()
    return ""


def _parse_include_entry(
    entry: Any, source_file: str = "", line: int = 0
) -> dict | None:
    include = _normalize_include(entry)
    for include_type, value in include.items():
        if include_type == "project":
            version = include.get("ref", "")
            return {
                "include_type": include_type,
                "project": value,
                "version": version,
                "valid_version": _include_valid_version(
                    version, include.get("file", ""), value
                ),
                "file": include.get("file", ""),
                "variables": include.get("variables", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
        if include_type == "component":
            try:
                project, version = value.split("@", 1)
            except ValueError:
                return None
            return {
                "include_type": include_type,
                "project": project,
                "version": version,
                "valid_version": _include_valid_version(version, "component", project),
                "file": "",
                "variables": include.get("inputs", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
        if include_type == "template":
            return {
                "include_type": include_type,
                "project": str(value),
                "version": "n/a",
                "valid_version": False,
                "file": "",
                "variables": {},
                "rules": [],
                "source_file": source_file,
                "line": line,
            }
        if include_type == "remote":
            version = _parse_remote_url_version(str(value))
            return {
                "include_type": include_type,
                "project": str(value),
                "version": version,
                "valid_version": _include_valid_version(version, "remote", str(value)),
                "file": "",
                "variables": {},
                "rules": [],
                "source_file": source_file,
                "line": line,
            }
        if include_type == "local":
            return {
                "include_type": include_type,
                "project": value,
                "version": "n/a",
                "valid_version": True,
                "file": "",
                "variables": include.get("variables", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
    return None


def _empty_image_defaults() -> dict[str, Any]:
    return {
        "image": "",
        "image_source_file": "",
        "image_line": 0,
        "services": None,
        "services_defined": False,
        "services_source_file": "",
        "services_line": 0,
    }


def _job_attribute_map(job: dict) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for attribute in job.get("attributes", []):
        key = attribute.get("key")
        if key:
            values[str(key)] = attribute.get("value")
    return values


def _extends_parent_names(values: dict[str, Any]) -> list[str]:
    raw = values.get("extends")
    if isinstance(raw, str) and raw:
        return [raw]
    if isinstance(raw, list):
        return [str(item) for item in raw if isinstance(item, str) and item]
    return []


def _service_items(services: Any) -> list[Any]:
    if services is None or services == "" or services == []:
        return []
    if isinstance(services, list):
        return list(services)
    return [services]


def _defaults_from_document(
    document: dict,
    defaults: dict[str, Any],
    source_file: str,
    line_index: dict | None,
) -> dict[str, Any]:
    """Fold one YAML document's global image keywords into *defaults*."""
    result = dict(defaults)
    globals_index = (line_index or {}).get("globals") or {}
    top_level = _parse_image_reference(document.get("image"))
    if top_level:
        result["image"] = top_level
        result["image_source_file"] = source_file
        result["image_line"] = int(globals_index.get("image_line") or 0)

    default_block = document.get("default")
    if not isinstance(default_block, dict):
        return result

    default_image = _parse_image_reference(default_block.get("image"))
    if default_image:
        result["image"] = default_image
        result["image_source_file"] = source_file
        result["image_line"] = int(globals_index.get("default_image_line") or 0)
    if "services" in default_block:
        result["services"] = default_block.get("services")
        result["services_defined"] = True
        result["services_source_file"] = source_file
        result["services_line"] = int(globals_index.get("default_services_line") or 0)
    return result


def _overlay_image_defaults(
    base: dict[str, Any] | None, overlay: dict[str, Any] | None
) -> dict[str, Any]:
    """Return *base* updated with set image and services values from *overlay*."""
    result = dict(base or _empty_image_defaults())
    if not overlay:
        return result
    if overlay.get("image"):
        result["image"] = overlay["image"]
        result["image_source_file"] = overlay.get("image_source_file", "")
        result["image_line"] = int(overlay.get("image_line") or 0)
    if overlay.get("services_defined"):
        result["services"] = overlay.get("services")
        result["services_defined"] = True
        result["services_source_file"] = overlay.get("services_source_file", "")
        result["services_line"] = int(overlay.get("services_line") or 0)
    return result


def _jobs_by_name(jobs: list[dict]) -> dict[str, dict]:
    named: dict[str, dict] = {}
    for job in jobs:
        name = str(job.get("name") or "")
        if name:
            named[name] = job
    return named


def _job_defining_keyword(
    job: dict,
    jobs_by_name: dict[str, dict],
    keyword: str,
    seen: set[str] | None = None,
) -> dict | None:
    """Return the job whose own config sets *keyword*, walking ``extends``."""
    if seen is None:
        seen = set()
    name = str(job.get("name") or "")
    if name in seen:
        return None
    if name:
        seen.add(name)
    values = _job_attribute_map(job)
    if keyword == "image" and _parse_image_reference(values.get("image")):
        return job
    if keyword == "services" and "services" in values:
        return job
    for parent_name in reversed(_extends_parent_names(values)):
        parent = jobs_by_name.get(parent_name)
        if not parent:
            continue
        found = _job_defining_keyword(parent, jobs_by_name, keyword, seen)
        if found:
            return found
    return None


def _image_row(
    *,
    image_ref: str,
    image_source: str,
    parent_job: str,
    source_file: str,
    line: int,
) -> dict:
    return {
        "include_type": "container_image",
        "image_source": image_source,
        "parent_job": parent_job,
        "project": image_ref,
        "image": image_ref,
        "version": "",
        "valid_version": False,
        "source_file": source_file,
        "line": line,
    }


def _collect_container_images(
    jobs: list[dict], defaults: dict[str, Any] | None = None
) -> list[dict]:
    """Effective runtime images for concrete jobs, including extends and default."""
    images: list[dict] = []
    jobs_by_name = _jobs_by_name(jobs)
    pipeline_defaults = defaults or _empty_image_defaults()

    for job in jobs:
        job_name = str(job.get("name") or "")
        if not job_name or job_name.startswith("."):
            continue
        values = _job_attribute_map(job)

        image_ref = ""
        image_source = ""
        source_file = str(job.get("source_file") or "")
        line = int(job.get("line") or 0)
        own_image = (
            _parse_image_reference(values.get("image")) if "image" in values else ""
        )
        if own_image:
            image_ref = own_image
            image_source = "job"
        else:
            defining = _job_defining_keyword(job, jobs_by_name, "image", set())
            if defining and defining is not job:
                inherited = _parse_image_reference(
                    _job_attribute_map(defining).get("image")
                )
                if inherited:
                    image_ref = inherited
                    image_source = "extends"
                    source_file = str(defining.get("source_file") or "")
                    line = int(defining.get("line") or 0)
        if not image_ref and pipeline_defaults.get("image"):
            image_ref = str(pipeline_defaults["image"])
            image_source = "default"
            source_file = str(pipeline_defaults.get("image_source_file") or "")
            line = int(pipeline_defaults.get("image_line") or 0)
        if image_ref:
            images.append(
                _image_row(
                    image_ref=image_ref,
                    image_source=image_source,
                    parent_job=job_name,
                    source_file=source_file,
                    line=line,
                )
            )

        if "services" in values:
            service_values = values.get("services")
            service_source = "service"
            service_file = str(job.get("source_file") or "")
            service_line = int(job.get("line") or 0)
        else:
            defining = _job_defining_keyword(job, jobs_by_name, "services", set())
            if defining and defining is not job:
                service_values = _job_attribute_map(defining).get("services")
                service_source = "extends"
                service_file = str(defining.get("source_file") or "")
                service_line = int(defining.get("line") or 0)
            elif pipeline_defaults.get("services_defined"):
                service_values = pipeline_defaults.get("services")
                service_source = "default"
                service_file = str(pipeline_defaults.get("services_source_file") or "")
                service_line = int(pipeline_defaults.get("services_line") or 0)
            else:
                service_values = None
                service_source = ""
                service_file = ""
                service_line = 0

        for service in _service_items(service_values):
            service_ref = _parse_service_image(service)
            if not service_ref:
                continue
            images.append(
                _image_row(
                    image_ref=service_ref,
                    image_source=service_source or "service",
                    parent_job=job_name,
                    source_file=service_file,
                    line=service_line,
                )
            )
    return images


def _parse_input_entry(key: str, value: Any) -> dict:
    description = ""
    options: Any = ""
    expand = True
    if isinstance(value, dict):
        description = value.get("description", "")
        options = value.get("options", "")
        expand = value.get("expand", True)
    return {
        "key": key,
        "value": value,
        "description": description,
        "options": options,
        "expand": expand,
    }


def _parse_variable_entry(
    key: str, value: Any, source_file: str = "", line: int = 0
) -> dict:
    description = ""
    options: Any = ""
    expand = True
    stored_value: Any = value
    if isinstance(value, dict):
        description = value.get("description", "")
        options = value.get("options", "")
        expand = value.get("expand", True)
        if "value" in value:
            stored_value = value["value"]
    return {
        "key": key,
        "value": stored_value,
        "description": description,
        "options": options,
        "expand": expand,
        "source_file": source_file,
        "line": line,
    }


def _parse_job(
    name: str,
    config: dict,
    source_file: str = "",
    line: int = 0,
    *,
    include_scripts: bool = False,
) -> dict:
    attributes = []
    nested = []
    rules = []
    scripts: dict[str, Any] = {}

    for key in sorted(config):
        if key in JOB_SKIP_ATTRIBUTES:
            if include_scripts and key in SCRIPT_ATTRIBUTE_KEYS:
                scripts[key] = config[key]
            continue
        value = config[key]
        if key == "rules" and isinstance(value, list):
            rules = value
            continue
        if key == "variables" and isinstance(value, dict):
            for item_key, item_value in value.items():
                nested.append({"attribute": key, "key": item_key, "value": item_value})
            continue
        if key == "needs" and isinstance(value, list):
            for item in value:
                nested.append({"attribute": key, "key": "", "value": item})
            continue
        attributes.append({"key": key, "value": value})

    job = {
        "name": name,
        "display_name": name.upper(),
        "is_template": name.startswith("."),
        "attributes": attributes,
        "rules": rules,
        "nested": nested,
        "source_file": source_file,
        "line": line,
    }
    if include_scripts:
        job.update(scripts)
        if "extends" in config:
            job["extends"] = config["extends"]
    return job


def _resolve_local_include_path(config_file: str, local_path: str) -> str | None:
    base_dir = os.path.realpath(os.path.dirname(os.path.abspath(config_file)))
    candidate = os.path.realpath(
        os.path.normpath(os.path.join(base_dir, local_path.lstrip("/")))
    )
    try:
        if os.path.commonpath([base_dir, candidate]) != base_dir:
            return None
    except ValueError:
        return None
    return candidate if os.path.exists(candidate) else None


def _should_resolve_external(
    resolve_external_includes: bool | None,
    *,
    include_type: str,
    token: str | None,
) -> bool:
    if resolve_external_includes is False:
        return False
    if resolve_external_includes is True:
        return include_type in {"remote", "project"}
    if include_type == "remote":
        return True
    if include_type == "project":
        return bool(token)
    return False


def _merge_nested_pipeline_data(target: dict[str, Any], nested: dict[str, Any]) -> None:
    target["includes"].extend(nested.get("includes", []))
    target["jobs"].extend(nested.get("jobs", []))
    target.setdefault("unresolved_includes", []).extend(
        nested.get("unresolved_includes", [])
    )
    target.setdefault("dynamic_child_pipelines", []).extend(
        nested.get("dynamic_child_pipelines", [])
    )
    target["nested_defaults"] = _overlay_image_defaults(
        target.get("nested_defaults"),
        nested.get("document_defaults"),
    )


def _job_trigger_value(job: dict[str, Any]) -> Any:
    for attribute in job.get("attributes", []):
        if attribute.get("key") == "trigger":
            return attribute.get("value")
    return None


def _parse_trigger_include_entry(
    entry: Any, source_file: str = "", line: int = 0
) -> dict | None:
    """Parse a ``trigger.include`` entry, including ``artifact`` generated YAML."""
    include = _normalize_include(entry)
    if not isinstance(include, dict):
        return None
    if "artifact" in include:
        artifact = str(include.get("artifact") or "").strip()
        if not artifact:
            return None
        return {
            "include_type": "artifact",
            "project": artifact,
            "artifact": artifact,
            "generator_job": str(include.get("job") or ""),
            "version": "n/a",
            "valid_version": True,
            "file": "",
            "variables": {},
            "rules": [],
            "source_file": source_file,
            "line": line,
        }
    return _parse_include_entry(entry, source_file=source_file, line=line)


def _path_inside_base(base_dir: str, candidate: str) -> bool:
    try:
        return os.path.commonpath([base_dir, candidate]) == base_dir
    except ValueError:
        return False


def _resolve_generated_artifact_path(
    config_file: str, artifact_path: str
) -> tuple[str | None, str]:
    """Resolve a generated artifact path relative to the pipeline dir, then cwd.

    Returns ``(resolved_path_or_none, reason)`` where reason is empty on success,
    ``path_rejected`` when the candidate escapes the base, or ``not_found``.
    """
    relative = str(artifact_path).lstrip("/")
    pipeline_dir = os.path.realpath(os.path.dirname(os.path.abspath(config_file)))
    cwd = os.path.realpath(os.getcwd())

    pipeline_candidate = os.path.realpath(
        os.path.normpath(os.path.join(pipeline_dir, relative))
    )
    if _path_inside_base(pipeline_dir, pipeline_candidate):
        if os.path.exists(pipeline_candidate):
            return pipeline_candidate, ""
    else:
        return None, "path_rejected"

    cwd_candidate = os.path.realpath(os.path.normpath(os.path.join(cwd, relative)))
    if _path_inside_base(cwd, cwd_candidate):
        if os.path.exists(cwd_candidate):
            return cwd_candidate, ""
    elif relative and not _path_inside_base(pipeline_dir, cwd_candidate):
        # cwd candidate escaped cwd; only reject when it also escapes pipeline dir
        if not _path_inside_base(pipeline_dir, cwd_candidate):
            return None, "path_rejected"

    return None, "not_found"


def _dynamic_child_record(
    *,
    trigger_job: str,
    generator_job: str,
    artifact: str,
    resolved: bool,
    source_file: str,
    line: int,
    include_type: str = "artifact",
) -> dict[str, Any]:
    return {
        "trigger_job": trigger_job,
        "generator_job": generator_job,
        "artifact": artifact,
        "resolved": resolved,
        "include_type": include_type,
        "source_file": source_file,
        "line": line,
    }


def _merge_generated_jobs(
    target: dict[str, Any],
    nested: dict[str, Any],
    *,
    parent_job: str,
    artifact: str,
) -> None:
    for job in nested.get("jobs", []):
        tagged = dict(job)
        tagged["dynamic_parent_job"] = parent_job
        tagged["generated_artifact"] = artifact
        target["jobs"].append(tagged)
    target["includes"].extend(nested.get("includes", []))
    target["variables"].extend(nested.get("variables", []))
    target.setdefault("dynamic_child_pipelines", []).extend(
        nested.get("dynamic_child_pipelines", [])
    )


def _collect_kwargs_for_nested(
    *,
    detailed: bool,
    include_nested: bool,
    max_include_depth: int | None,
    exclude_sections: set[str] | None,
    exclude_attributes: set[str] | None,
    group_by: str | None,
    include_scripts: bool,
    resolve_job_composition: bool,
    resolve_external_includes: bool | None,
    resolve_generated: bool,
    generated_configs: tuple[str, ...] | list[str] | None,
    gitlab_url: str | None,
    token: str | None,
) -> dict[str, Any]:
    return {
        "detailed": detailed,
        "include_nested": include_nested,
        "max_include_depth": max_include_depth,
        "exclude_sections": exclude_sections,
        "exclude_attributes": exclude_attributes,
        "group_by": group_by,
        "include_scripts": include_scripts,
        "resolve_job_composition": resolve_job_composition,
        "resolve_external_includes": resolve_external_includes,
        "resolve_generated": resolve_generated,
        "generated_configs": generated_configs,
        "gitlab_url": gitlab_url,
        "token": token,
    }


def _process_artifact_trigger_include(
    parsed: dict[str, Any],
    *,
    trigger_job: str,
    config_file: str,
    data: dict[str, Any],
    can_recurse: bool,
    include_nested: bool,
    collect_kwargs: dict[str, Any],
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
) -> None:
    artifact = str(parsed.get("artifact") or parsed.get("project") or "")
    generator_job = str(parsed.get("generator_job") or "")
    source_file = str(parsed.get("source_file") or config_file)
    line = int(parsed.get("line") or 0)

    if not can_recurse:
        reason = "include_nested_disabled" if not include_nested else "depth_exceeded"
        record_unresolved(_unresolved, parsed, reason=reason)
        data.setdefault("dynamic_child_pipelines", []).append(
            _dynamic_child_record(
                trigger_job=trigger_job,
                generator_job=generator_job,
                artifact=artifact,
                resolved=False,
                source_file=source_file,
                line=line,
            )
        )
        return

    resolved_path, fail_reason = _resolve_generated_artifact_path(config_file, artifact)
    if not resolved_path:
        gap_reason = (
            "path_rejected"
            if fail_reason == "path_rejected"
            else "generated_at_runtime"
        )
        record_unresolved(
            _unresolved,
            parsed,
            reason=gap_reason,
            detail=(
                f"trigger job {trigger_job} expects artifact {artifact}"
                if gap_reason == "generated_at_runtime"
                else ""
            ),
        )
        data.setdefault("dynamic_child_pipelines", []).append(
            _dynamic_child_record(
                trigger_job=trigger_job,
                generator_job=generator_job,
                artifact=artifact,
                resolved=False,
                source_file=source_file,
                line=line,
            )
        )
        return

    nested = collect_pipeline_data(
        resolved_path,
        **collect_kwargs,
        _depth=_depth + 1,
        _visited=_visited,
        _job_registry=_job_registry,
        _fetch_cache=_fetch_cache,
        _unresolved=_unresolved,
        _external_context=_external_context,
    )
    _merge_generated_jobs(
        data,
        nested,
        parent_job=trigger_job,
        artifact=artifact,
    )
    data.setdefault("dynamic_child_pipelines", []).append(
        _dynamic_child_record(
            trigger_job=trigger_job,
            generator_job=generator_job,
            artifact=artifact,
            resolved=True,
            source_file=source_file,
            line=line,
        )
    )


def _process_trigger_includes_for_jobs(
    jobs: list[dict[str, Any]],
    *,
    config_file: str,
    data: dict[str, Any],
    can_recurse: bool,
    include_nested: bool,
    detailed: bool,
    max_include_depth: int | None,
    exclude_sections: set[str] | None,
    exclude_attributes: set[str] | None,
    group_by: str | None,
    include_scripts: bool,
    resolve_job_composition: bool,
    resolve_external_includes: bool | None,
    resolve_generated: bool,
    generated_configs: tuple[str, ...] | list[str] | None,
    gitlab_url: str | None,
    token: str | None,
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
) -> None:
    if not resolve_generated:
        return

    collect_kwargs = _collect_kwargs_for_nested(
        detailed=detailed,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
        include_scripts=include_scripts,
        resolve_job_composition=resolve_job_composition,
        resolve_external_includes=resolve_external_includes,
        resolve_generated=resolve_generated,
        generated_configs=None,
        gitlab_url=gitlab_url,
        token=token,
    )

    for job in list(jobs):
        trigger = _job_trigger_value(job)
        if not isinstance(trigger, dict) or "include" not in trigger:
            continue
        trigger_job = str(job.get("name") or "")
        job_line = int(job.get("line") or 0)
        for entry in _iter_include_entries(trigger["include"]):
            parsed = _parse_trigger_include_entry(
                entry,
                source_file=str(job.get("source_file") or config_file),
                line=job_line,
            )
            if not parsed:
                continue
            if parsed.get("include_type") == "artifact":
                _process_artifact_trigger_include(
                    parsed,
                    trigger_job=trigger_job,
                    config_file=config_file,
                    data=data,
                    can_recurse=can_recurse,
                    include_nested=include_nested,
                    collect_kwargs=collect_kwargs,
                    _depth=_depth,
                    _visited=_visited,
                    _job_registry=_job_registry,
                    _fetch_cache=_fetch_cache,
                    _unresolved=_unresolved,
                    _external_context=_external_context,
                )
                continue

            # Static child pipeline includes (local/project/remote/…)
            data["includes"].append(parsed)
            local_resolved = False
            if parsed.get("include_type") == "local":
                local_resolved = bool(
                    _resolve_local_include_path(config_file, str(parsed.get("project")))
                )
            _process_parsed_include(
                parsed,
                config_file=config_file,
                data=data,
                can_recurse=can_recurse,
                include_nested=include_nested,
                detailed=detailed,
                max_include_depth=max_include_depth,
                exclude_sections=exclude_sections,
                exclude_attributes=exclude_attributes,
                group_by=group_by,
                include_scripts=include_scripts,
                resolve_job_composition=resolve_job_composition,
                resolve_external_includes=resolve_external_includes,
                resolve_generated=resolve_generated,
                generated_configs=None,
                gitlab_url=gitlab_url,
                token=token,
                _depth=_depth,
                _visited=_visited,
                _job_registry=_job_registry,
                _fetch_cache=_fetch_cache,
                _unresolved=_unresolved,
                _external_context=_external_context,
            )
            data.setdefault("dynamic_child_pipelines", []).append(
                _dynamic_child_record(
                    trigger_job=trigger_job,
                    generator_job="",
                    artifact=str(parsed.get("project") or parsed.get("file") or ""),
                    resolved=local_resolved and can_recurse and include_nested,
                    source_file=str(parsed.get("source_file") or config_file),
                    line=job_line,
                    include_type=str(parsed.get("include_type") or ""),
                )
            )


def _process_explicit_generated_configs(
    generated_configs: tuple[str, ...] | list[str] | None,
    *,
    config_file: str,
    data: dict[str, Any],
    collect_kwargs: dict[str, Any],
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
) -> None:
    if not generated_configs:
        return
    pipeline_dir = os.path.realpath(os.path.dirname(os.path.abspath(config_file)))
    for raw_path in generated_configs:
        path = str(raw_path).strip()
        if not path:
            continue
        parsed = {
            "include_type": "artifact",
            "project": path,
            "artifact": path,
            "generator_job": "",
            "source_file": config_file,
            "line": 0,
        }
        if os.path.isabs(path):
            candidate = os.path.realpath(path)
        else:
            candidate = os.path.realpath(
                os.path.normpath(os.path.join(pipeline_dir, path.lstrip("/")))
            )
            if not _path_inside_base(pipeline_dir, candidate):
                record_unresolved(_unresolved, parsed, reason="path_rejected")
                data.setdefault("dynamic_child_pipelines", []).append(
                    _dynamic_child_record(
                        trigger_job="",
                        generator_job="",
                        artifact=path,
                        resolved=False,
                        source_file=config_file,
                        line=0,
                    )
                )
                continue
        if not os.path.exists(candidate):
            record_unresolved(
                _unresolved,
                parsed,
                reason="generated_at_runtime",
                detail=f"explicit --generated-config {path}",
            )
            data.setdefault("dynamic_child_pipelines", []).append(
                _dynamic_child_record(
                    trigger_job="",
                    generator_job="",
                    artifact=path,
                    resolved=False,
                    source_file=config_file,
                    line=0,
                )
            )
            continue
        if candidate in _visited:
            continue
        nested = collect_pipeline_data(
            candidate,
            **collect_kwargs,
            _depth=_depth + 1,
            _visited=_visited,
            _job_registry=_job_registry,
            _fetch_cache=_fetch_cache,
            _unresolved=_unresolved,
            _external_context=_external_context,
        )
        _merge_generated_jobs(
            data,
            nested,
            parent_job="",
            artifact=path,
        )
        data.setdefault("dynamic_child_pipelines", []).append(
            _dynamic_child_record(
                trigger_job="",
                generator_job="",
                artifact=path,
                resolved=True,
                source_file=config_file,
                line=0,
            )
        )


def _collect_from_fetched_yaml(
    *,
    yaml_text: str,
    config_label: str,
    detailed: bool,
    include_nested: bool,
    max_include_depth: int | None,
    exclude_sections: set[str] | None,
    exclude_attributes: set[str] | None,
    group_by: str | None,
    include_scripts: bool,
    resolve_job_composition: bool,
    resolve_external_includes: bool | None,
    gitlab_url: str | None,
    token: str | None,
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    if config_label in _visited:
        return {
            "config_file": config_label,
            "inputs": [],
            "variables": [],
            "includes": [],
            "workflow_rules": [],
            "jobs": [],
            "container_images": [],
            "dynamic_child_pipelines": [],
            "job_registry": _job_registry,
            "unresolved_includes": [item.to_dict() for item in _unresolved],
            "line_index": {
                "jobs": {},
                "includes": [],
                "variables": {},
                "workflow_rules": [],
            },
        }
    _visited.add(config_label)

    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yml",
            delete=False,
            encoding="utf-8",
        ) as handle:
            handle.write(yaml_text)
            temp_path = handle.name
        return collect_pipeline_data(
            temp_path,
            detailed=detailed,
            include_nested=include_nested,
            max_include_depth=max_include_depth,
            exclude_sections=exclude_sections,
            exclude_attributes=exclude_attributes,
            group_by=group_by,
            include_scripts=include_scripts,
            resolve_job_composition=resolve_job_composition,
            resolve_external_includes=resolve_external_includes,
            resolve_generated=resolve_generated,
            generated_configs=generated_configs,
            gitlab_url=gitlab_url,
            token=token,
            _depth=_depth,
            _visited=_visited,
            _job_registry=_job_registry,
            _fetch_cache=_fetch_cache,
            _unresolved=_unresolved,
            _source_label=config_label,
            _external_context=_external_context,
        )
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _process_local_include(
    parsed: dict[str, Any],
    *,
    config_file: str,
    data: dict[str, Any],
    detailed: bool,
    include_nested: bool,
    max_include_depth: int | None,
    exclude_sections: set[str] | None,
    exclude_attributes: set[str] | None,
    group_by: str | None,
    include_scripts: bool,
    resolve_job_composition: bool,
    resolve_external_includes: bool | None,
    gitlab_url: str | None,
    token: str | None,
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
) -> None:
    if _external_context is not None:
        fetched = resolve_nested_local_from_context(
            str(parsed["project"]),
            _external_context,
            gitlab_url=default_gitlab_url(gitlab_url),
            token=token,
            cache=_fetch_cache,
        )
        if isinstance(fetched, IncludeFetchFailure):
            record_unresolved(
                _unresolved,
                parsed,
                reason=fetched.reason,
                detail=fetched.detail,
            )
            return
        nested_context: ExternalIncludeContext
        if _external_context.kind == "remote":
            from src.compliance.include_fetch import remote_directory_url

            nested_context = ExternalIncludeContext(
                kind="remote",
                visit_key=fetched.config_label,
                base_url=remote_directory_url(fetched.config_label),
            )
        else:
            nested_context = ExternalIncludeContext(
                kind="project",
                visit_key=fetched.config_label,
                project_path=_external_context.project_path,
                ref=_external_context.ref,
            )
        nested = _collect_from_fetched_yaml(
            yaml_text=fetched.yaml_text,
            config_label=fetched.config_label,
            detailed=detailed,
            include_nested=include_nested,
            max_include_depth=max_include_depth,
            exclude_sections=exclude_sections,
            exclude_attributes=exclude_attributes,
            group_by=group_by,
            include_scripts=include_scripts,
            resolve_job_composition=resolve_job_composition,
            resolve_external_includes=resolve_external_includes,
            resolve_generated=resolve_generated,
            generated_configs=generated_configs,
            gitlab_url=gitlab_url,
            token=token,
            _depth=_depth + 1,
            _visited=_visited,
            _job_registry=_job_registry,
            _fetch_cache=_fetch_cache,
            _unresolved=_unresolved,
            _external_context=nested_context,
        )
        _merge_nested_pipeline_data(data, nested)
        return

    sub_config = _resolve_local_include_path(config_file, parsed["project"])
    if not sub_config:
        base_dir = os.path.realpath(os.path.dirname(os.path.abspath(config_file)))
        candidate = os.path.realpath(
            os.path.normpath(os.path.join(base_dir, str(parsed["project"]).lstrip("/")))
        )
        try:
            outside_base = os.path.commonpath([base_dir, candidate]) != base_dir
        except ValueError:
            outside_base = True
        reason = "path_rejected" if outside_base else "not_found"
        record_unresolved(_unresolved, parsed, reason=reason)
        return
    nested = collect_pipeline_data(
        sub_config,
        detailed=detailed,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
        include_scripts=include_scripts,
        resolve_job_composition=resolve_job_composition,
        resolve_external_includes=resolve_external_includes,
        resolve_generated=resolve_generated,
        generated_configs=generated_configs,
        gitlab_url=gitlab_url,
        token=token,
        _depth=_depth + 1,
        _visited=_visited,
        _job_registry=_job_registry,
        _fetch_cache=_fetch_cache,
        _unresolved=_unresolved,
        _external_context=None,
    )
    _merge_nested_pipeline_data(data, nested)


def _process_parsed_include(
    parsed: dict[str, Any],
    *,
    config_file: str,
    data: dict[str, Any],
    can_recurse: bool,
    include_nested: bool,
    detailed: bool,
    max_include_depth: int | None,
    exclude_sections: set[str] | None,
    exclude_attributes: set[str] | None,
    group_by: str | None,
    include_scripts: bool,
    resolve_job_composition: bool,
    resolve_external_includes: bool | None,
    gitlab_url: str | None,
    token: str | None,
    _depth: int,
    _visited: set[str],
    _job_registry: dict[str, dict],
    _fetch_cache: IncludeFetchCache,
    _unresolved: list[UnresolvedInclude],
    _external_context: ExternalIncludeContext | None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
) -> None:
    include_type = parsed.get("include_type", "")
    if not can_recurse:
        reason = "include_nested_disabled" if not include_nested else "depth_exceeded"
        record_unresolved(_unresolved, parsed, reason=reason)
        return

    if include_type == "local":
        _process_local_include(
            parsed,
            config_file=config_file,
            data=data,
            detailed=detailed,
            include_nested=include_nested,
            max_include_depth=max_include_depth,
            exclude_sections=exclude_sections,
            exclude_attributes=exclude_attributes,
            group_by=group_by,
            include_scripts=include_scripts,
            resolve_job_composition=resolve_job_composition,
            resolve_external_includes=resolve_external_includes,
            resolve_generated=resolve_generated,
            generated_configs=generated_configs,
            gitlab_url=gitlab_url,
            token=token,
            _depth=_depth,
            _visited=_visited,
            _job_registry=_job_registry,
            _fetch_cache=_fetch_cache,
            _unresolved=_unresolved,
            _external_context=_external_context,
        )
        return

    if include_type in {"component", "template"}:
        record_unresolved(_unresolved, parsed, reason="unsupported_type")
        return

    if not _should_resolve_external(
        resolve_external_includes,
        include_type=include_type,
        token=token,
    ):
        if resolve_external_includes is False:
            reason = "external_resolution_disabled"
        elif include_type == "project":
            reason = "no_token"
        else:
            reason = "unsupported_type"
        record_unresolved(_unresolved, parsed, reason=reason)
        return

    fetched = fetch_include_content(
        parsed,
        gitlab_url=default_gitlab_url(gitlab_url),
        token=token,
        cache=_fetch_cache,
    )
    if isinstance(fetched, IncludeFetchFailure):
        record_unresolved(
            _unresolved,
            parsed,
            reason=fetched.reason,
            detail=fetched.detail,
        )
        return

    nested = _collect_from_fetched_yaml(
        yaml_text=fetched.yaml_text,
        config_label=fetched.config_label,
        detailed=detailed,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
        include_scripts=include_scripts,
        resolve_job_composition=resolve_job_composition,
        resolve_external_includes=resolve_external_includes,
        resolve_generated=resolve_generated,
        generated_configs=generated_configs,
        gitlab_url=gitlab_url,
        token=token,
        _depth=_depth + 1,
        _visited=_visited,
        _job_registry=_job_registry,
        _fetch_cache=_fetch_cache,
        _unresolved=_unresolved,
        _external_context=context_for_fetched(parsed, fetched),
    )
    _merge_nested_pipeline_data(data, nested)


def collect_pipeline_data(
    config_file: str,
    detailed: bool = False,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    exclude_sections: set[str] | None = None,
    exclude_attributes: set[str] | None = None,
    group_by: str | None = None,
    *,
    include_scripts: bool = False,
    resolve_job_composition: bool = False,
    resolve_external_includes: bool | None = None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    _depth: int = 0,
    _visited: set[str] | None = None,
    _job_registry: dict[str, dict] | None = None,
    _fetch_cache: IncludeFetchCache | None = None,
    _unresolved: list[UnresolvedInclude] | None = None,
    _source_label: str | None = None,
    _external_context: ExternalIncludeContext | None = None,
) -> dict:
    if resolve_job_composition:
        include_scripts = True

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    resolved_config = os.path.realpath(os.path.abspath(config_file))
    visited = _visited if _visited is not None else set()
    job_registry = _job_registry if _job_registry is not None else {}
    fetch_cache = _fetch_cache if _fetch_cache is not None else IncludeFetchCache()
    unresolved = _unresolved if _unresolved is not None else []
    if resolved_config in visited:
        return {
            "config_file": config_file,
            "inputs": [],
            "variables": [],
            "includes": [],
            "workflow_rules": [],
            "jobs": [],
            "container_images": [],
            "script_packages": [],
            "document_defaults": _empty_image_defaults(),
            "dynamic_child_pipelines": [],
            "job_registry": job_registry,
            "unresolved_includes": [item.to_dict() for item in unresolved],
            "line_index": {
                "jobs": {},
                "includes": [],
                "variables": {},
                "workflow_rules": [],
            },
        }
    visited.add(resolved_config)

    with open(config_file, encoding="utf-8") as handle:
        yaml_text = handle.read()
    documents = common.load_yml_documents(yaml_text)
    line_index = None
    try:
        from src.modules.yaml_lines import index_yaml_text

        line_index = index_yaml_text(yaml_text)
    except Exception:
        line_index = {
            "jobs": {},
            "includes": [],
            "variables": {},
            "workflow_rules": [],
            "globals": {},
        }

    skip_jobs = exclude_sections and "jobs" in exclude_sections

    data: dict[str, Any] = {
        "config_file": _source_label or config_file,
        "inputs": [],
        "variables": [],
        "includes": [],
        "workflow_rules": [],
        "jobs": [],
        "container_images": [],
        "script_packages": [],
        "dynamic_child_pipelines": [],
        "unresolved_includes": [],
    }

    local_defaults = _empty_image_defaults()
    for document in documents:
        if isinstance(document, dict):
            local_defaults = _defaults_from_document(
                document, local_defaults, config_file, line_index
            )

    can_recurse = include_nested and (
        max_include_depth is None or _depth < max_include_depth
    )

    for document in documents:
        if not isinstance(document, dict):
            continue
        if exclude_sections and "inputs" in exclude_sections:
            pass
        elif "spec" in document and "inputs" in document["spec"]:
            for key, value in document["spec"]["inputs"].items():
                data["inputs"].append(_parse_input_entry(key, value))

        if exclude_sections and "variables" in exclude_sections:
            pass
        elif "variables" in document:
            for key, value in document["variables"].items():
                data["variables"].append(
                    _parse_variable_entry(
                        key,
                        value,
                        source_file=config_file,
                        line=line_index["variables"].get(key, 0),
                    )
                )

        if exclude_sections and "includes" in exclude_sections:
            pass
        elif "include" in document:
            for index, entry in enumerate(_iter_include_entries(document["include"])):
                include_line = (
                    line_index["includes"][index]
                    if index < len(line_index["includes"])
                    else 0
                )
                parsed = _parse_include_entry(
                    entry, source_file=config_file, line=include_line
                )
                if parsed:
                    data["includes"].append(parsed)
                    _process_parsed_include(
                        parsed,
                        config_file=config_file,
                        data=data,
                        can_recurse=can_recurse,
                        include_nested=include_nested,
                        detailed=detailed,
                        max_include_depth=max_include_depth,
                        exclude_sections=exclude_sections,
                        exclude_attributes=exclude_attributes,
                        group_by=group_by,
                        include_scripts=include_scripts,
                        resolve_job_composition=resolve_job_composition,
                        resolve_external_includes=resolve_external_includes,
                        resolve_generated=resolve_generated,
                        generated_configs=None,
                        gitlab_url=gitlab_url,
                        token=token,
                        _depth=_depth,
                        _visited=visited,
                        _job_registry=job_registry,
                        _fetch_cache=fetch_cache,
                        _unresolved=unresolved,
                        _external_context=_external_context,
                    )

        if exclude_sections and "workflow" in exclude_sections:
            pass
        elif detailed and "workflow" in document:
            workflow = document["workflow"]
            if isinstance(workflow, dict) and "rules" in workflow:
                data["workflow_rules"] = workflow["rules"]
            elif isinstance(workflow, list):
                data["workflow_rules"] = workflow

        if not skip_jobs:
            for key, value in document.items():
                if key in JOB_EXCLUDE_KEYWORDS and not key.startswith("."):
                    continue
                if not isinstance(value, dict):
                    continue
                job_line = line_index["jobs"].get(key, 0)
                if include_scripts or resolve_job_composition:
                    register_job_entry(
                        job_registry,
                        job_name=key,
                        config=value,
                        source_file=config_file,
                        line=job_line,
                    )
                data["jobs"].append(
                    _parse_job(
                        key,
                        value,
                        source_file=config_file,
                        line=job_line,
                        include_scripts=include_scripts,
                    )
                )

    if not skip_jobs:
        jobs_before_dynamic = list(data["jobs"])
        _process_trigger_includes_for_jobs(
            jobs_before_dynamic,
            config_file=config_file,
            data=data,
            can_recurse=can_recurse,
            include_nested=include_nested,
            detailed=detailed,
            max_include_depth=max_include_depth,
            exclude_sections=exclude_sections,
            exclude_attributes=exclude_attributes,
            group_by=group_by,
            include_scripts=include_scripts,
            resolve_job_composition=resolve_job_composition,
            resolve_external_includes=resolve_external_includes,
            resolve_generated=resolve_generated,
            generated_configs=None,
            gitlab_url=gitlab_url,
            token=token,
            _depth=_depth,
            _visited=visited,
            _job_registry=job_registry,
            _fetch_cache=fetch_cache,
            _unresolved=unresolved,
            _external_context=_external_context,
        )

    if _depth == 0 and resolve_generated and generated_configs:
        _process_explicit_generated_configs(
            generated_configs,
            config_file=config_file,
            data=data,
            collect_kwargs=_collect_kwargs_for_nested(
                detailed=detailed,
                include_nested=include_nested,
                max_include_depth=max_include_depth,
                exclude_sections=exclude_sections,
                exclude_attributes=exclude_attributes,
                group_by=group_by,
                include_scripts=include_scripts,
                resolve_job_composition=resolve_job_composition,
                resolve_external_includes=resolve_external_includes,
                resolve_generated=resolve_generated,
                generated_configs=None,
                gitlab_url=gitlab_url,
                token=token,
            ),
            _depth=_depth,
            _visited=visited,
            _job_registry=job_registry,
            _fetch_cache=fetch_cache,
            _unresolved=unresolved,
            _external_context=_external_context,
        )

    effective_defaults = _overlay_image_defaults(
        data.get("nested_defaults"), local_defaults
    )
    data["document_defaults"] = effective_defaults
    if not skip_jobs and not (
        exclude_sections and "container_images" in exclude_sections
    ):
        data["container_images"] = _collect_container_images(
            data["jobs"], effective_defaults
        )
    data["line_index"] = line_index
    data["job_registry"] = job_registry
    data["unresolved_includes"] = [item.to_dict() for item in unresolved]

    if resolve_job_composition and _depth == 0 and job_registry:
        from src.modules.job_composition import effective_scripts_as_values

        composed_jobs = []
        for job in data["jobs"]:
            effective = compose_job_scripts(
                job["name"],
                job_registry,
                source_file=job.get("source_file", config_file),
            )
            values = effective_scripts_as_values(effective)
            enriched = dict(job)
            enriched.update(
                {
                    "before_script": values["before_script"],
                    "script": values["script"],
                    "after_script": values["after_script"],
                    "effective_script": values["effective_script"],
                    "extends_chain": values["extends_chain"],
                    "unresolved_script_references": values[
                        "unresolved_script_references"
                    ],
                    "script_provenance": values["script_provenance"],
                }
            )
            composed_jobs.append(enriched)
        data["jobs"] = composed_jobs
        data["merged_jobs"] = composed_jobs
        from src.compliance.script_analysis import extract_script_packages

        packages: list[dict] = []
        for job in composed_jobs:
            if str(job.get("name") or "").startswith("."):
                continue
            packages.extend(extract_script_packages(job))
        data["script_packages"] = packages

    return apply_output_filters(
        data,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
    )
