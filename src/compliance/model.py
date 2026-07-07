"""Load GitLab CI YAML into compliance entity stash."""

from __future__ import annotations

import os
from typing import Any

from src.modules.pipeline_data import collect_pipeline_data


def _job_entity(name: str, config: dict, source_file: str = "", line: int = 0) -> dict:
    return {
        "address": f"job.{name}",
        "type": "job",
        "name": name,
        "values": dict(config),
        "source_file": source_file,
        "line": line,
    }


def _include_entity(index: int, include: dict) -> dict:
    version = include.get("version", "")
    return {
        "address": f"include.{index}",
        "type": "include",
        "include_type": include["include_type"],
        "name": include.get("project", ""),
        "project": include.get("project", ""),
        "version": version,
        "valid_version": include.get("valid_version", False),
        "latest_version": include.get("latest_version", ""),
        "update_available": include.get("update_available", False),
        "release_metadata_resolved": include.get("release_metadata_resolved", False),
        "version_released_at": include.get("version_released_at", ""),
        "latest_version_released_at": include.get("latest_version_released_at", ""),
        "latest_release_age_days": include.get("latest_release_age_days"),
        "release_lag_days": include.get("release_lag_days"),
        "version_tag_rank": include.get("version_tag_rank"),
        "semver_tag_count": include.get("semver_tag_count", 0),
        "file": include.get("file", ""),
        "values": include,
        "source_file": include.get("source_file", ""),
        "line": include.get("line", 0),
    }


def _container_image_entity(index: int, image: dict) -> dict:
    image_ref = image.get("image", image.get("project", ""))
    return {
        "address": f"container_image.{index}",
        "type": "container_image",
        "include_type": "container_image",
        "image_source": image.get("image_source", ""),
        "parent_job": image.get("parent_job", ""),
        "name": image_ref,
        "project": image_ref,
        "image": image_ref,
        "version": image.get("version", ""),
        "valid_version": image.get("valid_version", False),
        "registry": image.get("registry", ""),
        "repository": image.get("repository", ""),
        "digest": image.get("digest", ""),
        "latest_version": image.get("latest_version", ""),
        "latest_digest": image.get("latest_digest", ""),
        "update_available": image.get("update_available", False),
        "release_metadata_resolved": image.get("release_metadata_resolved", False),
        "latest_release_age_days": image.get("latest_release_age_days"),
        "release_lag_days": image.get("release_lag_days"),
        "version_tag_rank": image.get("version_tag_rank"),
        "semver_tag_count": image.get("semver_tag_count", 0),
        "values": image,
        "source_file": image.get("source_file", ""),
        "line": image.get("line", 0),
    }


def _variable_entity(
    key: str, value: Any, source_file: str = "", line: int = 0
) -> dict:
    return {
        "address": f"variable.{key}",
        "type": "variable",
        "name": key,
        "key": key,
        "value": value,
        "values": {"value": value},
        "source_file": source_file,
        "line": line,
    }


def _workflow_rule_entity(
    index: int, rule: Any, source_file: str = "", line: int = 0
) -> dict:
    return {
        "address": f"workflow.rule.{index}",
        "type": "workflow_rule",
        "name": f"rule-{index}",
        "values": rule if isinstance(rule, dict) else {"rule": rule},
        "source_file": source_file,
        "line": line,
    }


def load_yaml_entities(
    pipeline_file: str,
    include_nested: bool = True,
) -> dict[str, list[dict]]:
    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    pipeline_data = collect_pipeline_data(
        config_file=pipeline_file,
        detailed=True,
        include_nested=include_nested,
    )

    line_index = pipeline_data.get("line_index") or {}
    workflow_rule_lines = line_index.get("workflow_rules", [])

    entities: dict[str, list[dict]] = {
        "jobs": [
            _job_entity(
                job["name"],
                _job_values(job),
                job.get("source_file", pipeline_file),
                job.get("line", 0),
            )
            for job in pipeline_data["jobs"]
        ],
        "includes": [
            _include_entity(index, include)
            for index, include in enumerate(pipeline_data["includes"])
        ],
        "variables": [
            _variable_entity(
                item["key"],
                item["value"],
                item.get("source_file", pipeline_file),
                item.get("line", 0),
            )
            for item in pipeline_data["variables"]
        ],
        "workflow_rules": [
            _workflow_rule_entity(
                index,
                rule,
                pipeline_file,
                (
                    workflow_rule_lines[index - 1]
                    if index - 1 < len(workflow_rule_lines)
                    else 0
                ),
            )
            for index, rule in enumerate(pipeline_data["workflow_rules"], 1)
        ],
        "project_settings": [],
        "project_ci_variables": [],
        "group_settings": [],
        "container_images": [
            _container_image_entity(index, image)
            for index, image in enumerate(pipeline_data["container_images"], 1)
        ],
    }
    return entities


def _job_values(job: dict) -> dict:
    values = {}
    for attribute in job.get("attributes", []):
        values[attribute["key"]] = attribute["value"]
    if job.get("rules"):
        values["rules"] = job["rules"]
    for nested in job.get("nested", []):
        if nested["attribute"] == "variables":
            values.setdefault("variables", {})
            values["variables"][nested["key"]] = nested["value"]
        elif nested["attribute"] == "needs":
            values.setdefault("needs", [])
            values["needs"].append(nested["value"])
    return values


def load_pipeline_entities(
    pipeline_file: str,
    include_nested: bool = True,
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    group: str | None = None,
    enrich_includes: bool = True,
    enrich_images: bool = True,
    load_api_entities: bool = True,
) -> dict[str, list[dict]]:
    from src.compliance.api_config import (resolve_group, resolve_project,
                                           resolve_token)
    from src.compliance.release_cache import ReleaseMetadataCache

    entities = load_yaml_entities(pipeline_file, include_nested=include_nested)

    userdata = {
        "project": project or "",
        "group": group or "",
    }
    api_token = token or resolve_token(userdata)
    resolved_project = resolve_project(userdata)
    resolved_group = resolve_group(userdata)

    cache = ReleaseMetadataCache()
    gl = None
    resolved_gitlab_url = (
        gitlab_url
        or os.getenv("CI_SERVER_URL")
        or os.getenv("GITLAB_URL")
        or "https://gitlab.com"
    )

    needs_gitlab_client = api_token and (
        enrich_includes
        or enrich_images
        or (load_api_entities and (resolved_project or resolved_group))
    )
    if needs_gitlab_client:
        try:
            import gitlab

            gl = gitlab.Gitlab(resolved_gitlab_url, private_token=api_token)
            gl.auth()
        except Exception:
            gl = None

    if api_token and enrich_includes:
        from src.compliance.include_versions import enrich_includes_with_releases

        enriched_includes = enrich_includes_with_releases(
            [include["values"] for include in entities["includes"]],
            gitlab_url=gitlab_url,
            token=api_token,
            gl=gl,
            cache=cache,
        )
        entities["includes"] = [
            _include_entity(index, include)
            for index, include in enumerate(enriched_includes)
        ]

    if api_token and enrich_images:
        from src.compliance.image_versions import enrich_container_images_with_releases

        enriched_images = enrich_container_images_with_releases(
            [image["values"] for image in entities["container_images"]],
            gitlab_url=gitlab_url,
            token=api_token,
            cache=cache,
        )
        entities["container_images"] = [
            _container_image_entity(index, image)
            for index, image in enumerate(enriched_images, 1)
        ]

    if api_token and load_api_entities and (resolved_project or resolved_group) and gl:
        from src.compliance.gitlab_api import load_api_entities as fetch_api_entities

        api_entities = fetch_api_entities(
            gitlab_url=gitlab_url,
            token=api_token,
            project=resolved_project,
            group=resolved_group,
            gl=gl,
        )
        entities["project_settings"].extend(api_entities.get("project_settings", []))
        entities["project_ci_variables"].extend(
            api_entities.get("project_ci_variables", [])
        )
        entities["group_settings"].extend(api_entities.get("group_settings", []))

    return entities
