"""Render a pipeline component inventory as CycloneDX 1.6 JSON."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from src import __version__
from src.compliance.sbom import (
    build_purl,
    components_from_pipeline,
    load_pipeline_inventory,
)


def _occurrence_payload(occurrence: dict) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    location = str(occurrence.get("location") or "")
    if location:
        payload["location"] = location
    line = int(occurrence.get("line") or 0)
    if line:
        payload["line"] = line
    context = str(occurrence.get("context") or "")
    if context:
        payload["additionalContext"] = context
    return payload


def _component_payload(component: dict) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": component.get("type") or "library",
        "name": component.get("name") or "component",
        "bom-ref": component["purl"],
        "purl": component["purl"],
    }
    version = str(component.get("version") or "")
    if version:
        payload["version"] = version
    hashes = [item for item in component.get("hashes") or [] if item]
    if hashes:
        payload["hashes"] = [{"alg": "SHA-256", "content": digest} for digest in hashes]
    properties = component.get("properties") or {}
    rendered_properties = [
        {"name": key, "value": str(value)}
        for key, value in sorted(properties.items())
        if value not in ("", None)
    ]
    if rendered_properties:
        payload["properties"] = rendered_properties
    references = component.get("external_references") or []
    if references:
        payload["externalReferences"] = references
    occurrences = [
        _occurrence_payload(item)
        for item in component.get("occurrences") or []
        if _occurrence_payload(item)
    ]
    if occurrences:
        payload["evidence"] = {"occurrences": occurrences}
    return payload


def render_cyclonedx_document(
    components: list[dict],
    *,
    pipeline_file: str,
    project: str | None = None,
    serial_number: str | None = None,
    timestamp: str | None = None,
) -> dict:
    """Return a CycloneDX 1.6 document for *components*."""
    pipeline_name = os.path.basename(pipeline_file) or "gitlab-ci.yml"
    metadata_properties = []
    if project:
        metadata_properties.append(
            {"name": "gitlab-compliance:project", "value": str(project)}
        )
    metadata_component: dict[str, Any] = {
        "type": "application",
        "name": pipeline_name,
        "bom-ref": "pipeline",
        "purl": build_purl("generic", pipeline_name),
    }
    if metadata_properties:
        metadata_component["properties"] = metadata_properties

    rendered = [_component_payload(component) for component in components]
    document: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": serial_number or f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": timestamp
            or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "gitlab-compliance",
                        "version": __version__,
                    }
                ]
            },
            "component": metadata_component,
        },
        "components": rendered,
        "dependencies": [
            {
                "ref": "pipeline",
                "dependsOn": [component["purl"] for component in components],
            }
        ],
    }
    return document


def render_cyclonedx(document: dict) -> str:
    """Serialize a CycloneDX document as JSON."""
    return json.dumps(document, indent=2, sort_keys=False) + "\n"


def build_cyclonedx_sbom(
    pipeline_file: str,
    *,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    resolve_external_includes: bool | None = None,
    resolve_generated: bool = True,
    generated_configs: tuple[str, ...] | list[str] | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    resolve: bool = False,
    serial_number: str | None = None,
    timestamp: str | None = None,
) -> str:
    """Collect a pipeline and return its CycloneDX SBOM."""
    data = load_pipeline_inventory(
        pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        resolve_external_includes=resolve_external_includes,
        resolve_generated=resolve_generated,
        generated_configs=generated_configs,
        gitlab_url=gitlab_url,
        token=token,
        resolve=resolve,
    )
    components = components_from_pipeline(data, pipeline_file)
    document = render_cyclonedx_document(
        components,
        pipeline_file=pipeline_file,
        project=project,
        serial_number=serial_number,
        timestamp=timestamp,
    )
    return render_cyclonedx(document)
