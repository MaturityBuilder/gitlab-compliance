"""Detect which API-backed enrichment steps a policy pack requires."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class ApiEnrichmentRequirements:
    enrich_includes: bool = False
    enrich_images: bool = False
    load_api_entities: bool = False


INCLUDE_MARKERS = (
    "include with release metadata",
    "newer release",
    "within the latest",
)

IMAGE_MARKERS = (
    "container image with release metadata",
    "registry latest",
)

API_ENTITY_MARKERS = (
    "project setting",
    "project ci variable",
    "group setting",
)


def policies_require_api_enrichment(features_dir: str) -> ApiEnrichmentRequirements:
    reqs = ApiEnrichmentRequirements()
    if not os.path.isdir(features_dir):
        return reqs

    combined: list[str] = []
    for root, _dirs, files in os.walk(features_dir):
        for filename in files:
            if not filename.endswith(".feature"):
                continue
            feature_path = os.path.join(root, filename)
            with open(feature_path, encoding="utf-8") as handle:
                combined.append(handle.read().lower())

    text = "\n".join(combined)
    reqs.enrich_includes = any(marker in text for marker in INCLUDE_MARKERS)
    reqs.enrich_images = any(marker in text for marker in IMAGE_MARKERS)
    reqs.load_api_entities = any(marker in text for marker in API_ENTITY_MARKERS)
    return reqs
