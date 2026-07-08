"""Detect which API-backed enrichment steps a policy pack requires."""

from __future__ import annotations

import os
from dataclasses import dataclass

from src.compliance.metadata import iter_feature_files


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


def policies_require_api_enrichment(
    features_dirs: str | list[str],
) -> ApiEnrichmentRequirements:
    reqs = ApiEnrichmentRequirements()
    directories = [features_dirs] if isinstance(features_dirs, str) else features_dirs

    for features_dir in directories:
        if not os.path.isdir(features_dir):
            continue
        for feature_path in iter_feature_files(features_dir):
            with open(feature_path, encoding="utf-8") as handle:
                text = handle.read().lower()
            if not reqs.enrich_includes:
                reqs.enrich_includes = any(marker in text for marker in INCLUDE_MARKERS)
            if not reqs.enrich_images:
                reqs.enrich_images = any(marker in text for marker in IMAGE_MARKERS)
            if not reqs.load_api_entities:
                reqs.load_api_entities = any(
                    marker in text for marker in API_ENTITY_MARKERS
                )
            if reqs.enrich_includes and reqs.enrich_images and reqs.load_api_entities:
                return reqs

    return reqs
