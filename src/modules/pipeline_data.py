"""Collect structured pipeline documentation from GitLab CI YAML."""

from __future__ import annotations

import os
import re
from typing import Any

import src.modules.common as common
from src.compliance.include_versions import is_valid_semver_version
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


def _collect_container_images(jobs: list[dict]) -> list[dict]:
    images: list[dict] = []
    index = 0
    for job in jobs:
        job_name = job.get("name", "")
        source_file = job.get("source_file", "")
        job_line = job.get("line", 0)
        values = {}
        for attribute in job.get("attributes", []):
            values[attribute["key"]] = attribute["value"]

        image_ref = _parse_image_reference(values.get("image"))
        if image_ref:
            index += 1
            images.append(
                {
                    "include_type": "container_image",
                    "image_source": "job",
                    "parent_job": job_name,
                    "project": image_ref,
                    "image": image_ref,
                    "version": "",
                    "valid_version": False,
                    "source_file": source_file,
                    "line": job_line,
                }
            )

        services = values.get("services", [])
        if isinstance(services, list):
            for service in services:
                service_ref = _parse_service_image(service)
                if not service_ref:
                    continue
                index += 1
                images.append(
                    {
                        "include_type": "container_image",
                        "image_source": "service",
                        "parent_job": job_name,
                        "project": service_ref,
                        "image": service_ref,
                        "version": "",
                        "valid_version": False,
                        "source_file": source_file,
                        "line": job_line,
                    }
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
    _depth: int = 0,
    _visited: set[str] | None = None,
    _job_registry: dict[str, dict] | None = None,
) -> dict:
    if resolve_job_composition:
        include_scripts = True

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    resolved_config = os.path.realpath(os.path.abspath(config_file))
    visited = _visited if _visited is not None else set()
    job_registry = _job_registry if _job_registry is not None else {}
    if resolved_config in visited:
        return {
            "config_file": config_file,
            "inputs": [],
            "variables": [],
            "includes": [],
            "workflow_rules": [],
            "jobs": [],
            "container_images": [],
            "job_registry": job_registry,
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
        line_index = {"jobs": {}, "includes": [], "variables": {}, "workflow_rules": []}

    skip_jobs = exclude_sections and "jobs" in exclude_sections

    data: dict[str, Any] = {
        "config_file": config_file,
        "inputs": [],
        "variables": [],
        "includes": [],
        "workflow_rules": [],
        "jobs": [],
        "container_images": [],
    }

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
            for index, entry in enumerate(document["include"]):
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
                    if can_recurse and parsed["include_type"] == "local":
                        sub_config = _resolve_local_include_path(
                            config_file, parsed["project"]
                        )
                        if sub_config:
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
                                _depth=_depth + 1,
                                _visited=visited,
                                _job_registry=job_registry,
                            )
                            data["includes"].extend(nested["includes"])
                            data["jobs"].extend(nested["jobs"])

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
                    job_registry[key] = {
                        "config": value,
                        "source_file": config_file,
                        "line": job_line,
                    }
                data["jobs"].append(
                    _parse_job(
                        key,
                        value,
                        source_file=config_file,
                        line=job_line,
                        include_scripts=include_scripts,
                    )
                )

    if not skip_jobs and not (
        exclude_sections and "container_images" in exclude_sections
    ):
        data["container_images"] = _collect_container_images(data["jobs"])
    data["line_index"] = line_index
    data["job_registry"] = job_registry

    if resolve_job_composition and _depth == 0 and job_registry:
        from src.modules.job_composition import (
            compose_job_scripts,
            effective_scripts_as_values,
        )

        composed_jobs = []
        for job in data["jobs"]:
            effective = compose_job_scripts(job["name"], job_registry)
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

    return apply_output_filters(
        data,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
    )
