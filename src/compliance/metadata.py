"""Parse Conftest-style # METADATA annotations from compliance policy files."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from src.compliance.api_enrichment import ApiEnrichmentRequirements

METADATA_MARKER = "# METADATA"


@dataclass
class PolicyAnnotation:
    policy_id: str
    title: str
    description: str = ""
    scope: str = ""
    feature_file: str = ""
    line: int = 0
    feature_name: str = ""
    scenario_name: str = ""
    custom: dict = field(default_factory=dict)


def format_custom_list(custom: dict | None, key: str) -> str:
    """Format a custom list/scalar metadata field as a comma-separated string."""
    if not custom:
        return ""
    value = custom.get(key)
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value if item is not None and str(item))
    return str(value)


@dataclass
class FeaturePolicies:
    feature_file: str
    feature_name: str
    annotation: PolicyAnnotation | None = None
    scenarios: list[PolicyAnnotation] = field(default_factory=list)


@dataclass
class PolicyCatalog:
    features: list[FeaturePolicies] = field(default_factory=list)

    def lookup_scenario(
        self, feature_file: str, scenario_name: str
    ) -> PolicyAnnotation | None:
        normalized = os.path.realpath(feature_file)
        normalized_name = normalize_scenario_name(scenario_name)
        for feature in self.features:
            if os.path.realpath(feature.feature_file) != normalized:
                continue
            for scenario in feature.scenarios:
                if scenario.scenario_name in (scenario_name, normalized_name):
                    return scenario
        return None


def normalize_scenario_name(scenario_name: str) -> str:
    """Strip Behave Scenario Outline example suffixes for metadata lookup."""
    return re.sub(r"\s+--\s+@\d+(?:\.\d+)?(?:\s+.*)?$", "", scenario_name).strip()


def iter_feature_files(
    features_dir: str, *, sort_names: bool = False, recursive: bool = True
) -> Iterator[str]:
    """Yield paths to .feature files under a policy directory."""
    if recursive:
        for root, _dirs, files in os.walk(features_dir):
            names = sorted(files) if sort_names else files
            for filename in names:
                if filename.endswith(".feature"):
                    yield os.path.join(root, filename)
        return

    names = (
        sorted(os.listdir(features_dir))
        if sort_names
        else list(os.listdir(features_dir))
    )
    for filename in names:
        if filename.endswith(".feature"):
            yield os.path.join(features_dir, filename)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").upper()
    return slug or "POLICY"


def _auto_feature_id(feature_file: str) -> str:
    return f"GLCI-{_slug(Path(feature_file).stem)}"


def _auto_scenario_id(feature_id: str, index: int) -> str:
    return f"{feature_id}-{index:03d}"


def _quote_yaml_scalar(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _prepare_metadata_yaml_line(line: str) -> str:
    if line.startswith("  "):
        return line
    if ":" not in line:
        return line
    key, sep, rest = line.partition(":")
    value = rest.strip()
    if not value or value in ("|", ">"):
        return line
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return line
    if ":" in value:
        return f"{key}{sep} {_quote_yaml_scalar(value)}"
    return line


def _parse_metadata_yaml(yaml_lines: list[str]) -> dict:
    if not yaml_lines:
        return {}
    prepared = [_prepare_metadata_yaml_line(line) for line in yaml_lines]
    parsed = yaml.safe_load("\n".join(prepared))
    return parsed if isinstance(parsed, dict) else {}


def _collect_metadata_block(lines: list[str], start_index: int) -> tuple[dict, int]:
    yaml_lines: list[str] = []
    index = start_index + 1
    while index < len(lines):
        line = lines[index]
        if line.startswith("# "):
            yaml_lines.append(line[2:])
            index += 1
            continue
        break
    return _parse_metadata_yaml(yaml_lines), index


def _annotation_from_raw(
    raw: dict,
    *,
    scope: str,
    feature_file: str,
    line: int,
    feature_name: str,
    scenario_name: str = "",
    default_title: str,
    default_id: str,
) -> PolicyAnnotation:
    custom = raw.get("custom", {})
    if not isinstance(custom, dict):
        custom = {}

    policy_id = str(custom.get("id") or raw.get("id") or default_id)
    title = str(raw.get("title") or default_title)
    description = str(raw.get("description") or "")

    return PolicyAnnotation(
        policy_id=policy_id,
        title=title,
        description=description,
        scope=scope,
        feature_file=feature_file,
        line=line,
        feature_name=feature_name,
        scenario_name=scenario_name,
        custom=custom,
    )


def parse_feature_policies(
    feature_file: str, *, text: str | None = None
) -> FeaturePolicies:
    feature_path = os.path.realpath(feature_file)
    if text is None:
        with open(feature_path, encoding="utf-8") as handle:
            text = handle.read()
    lines = text.splitlines()

    pending_metadata: dict = {}
    feature_name = Path(feature_path).stem
    feature_annotation: PolicyAnnotation | None = None
    scenarios: list[PolicyAnnotation] = []
    scenario_index = 0

    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(METADATA_MARKER):
            pending_metadata, index = _collect_metadata_block(lines, index)
            continue

        if line.startswith("Feature:"):
            feature_name = line.split(":", 1)[1].strip() or feature_name
            feature_id = _auto_feature_id(feature_path)
            feature_annotation = _annotation_from_raw(
                pending_metadata,
                scope="feature",
                feature_file=feature_path,
                line=index + 1,
                feature_name=feature_name,
                default_title=feature_name,
                default_id=feature_id,
            )
            pending_metadata = {}
            index += 1
            continue

        stripped = line.strip()
        scenario_prefix = None
        if stripped.startswith("Scenario Outline:"):
            scenario_prefix = "Scenario Outline:"
        elif stripped.startswith("Scenario:"):
            scenario_prefix = "Scenario:"

        if scenario_prefix:
            scenario_name = stripped.split(":", 1)[1].strip()
            scenario_index += 1
            feature_id = (
                feature_annotation.policy_id
                if feature_annotation
                else _auto_feature_id(feature_path)
            )
            scenarios.append(
                _annotation_from_raw(
                    pending_metadata,
                    scope="scenario",
                    feature_file=feature_path,
                    line=index + 1,
                    feature_name=feature_name,
                    scenario_name=scenario_name,
                    default_title=scenario_name,
                    default_id=_auto_scenario_id(feature_id, scenario_index),
                )
            )
            pending_metadata = {}
            index += 1
            continue

        index += 1

    if feature_annotation is None:
        feature_id = _auto_feature_id(feature_path)
        feature_annotation = PolicyAnnotation(
            policy_id=feature_id,
            title=feature_name,
            scope="feature",
            feature_file=feature_path,
            line=1,
            feature_name=feature_name,
        )

    return FeaturePolicies(
        feature_file=feature_path,
        feature_name=feature_name,
        annotation=feature_annotation,
        scenarios=scenarios,
    )


def build_policy_catalog(features_dir: str) -> PolicyCatalog:
    return build_policy_catalog_from_dirs([features_dir])


def build_policy_catalog_from_dirs(features_dirs: list[str]) -> PolicyCatalog:
    return discover_policies(features_dirs).catalog


@dataclass(frozen=True)
class PolicyRoot:
    """One policy directory and whether to walk nested subdirectories."""

    path: str
    recursive: bool = True


@dataclass
class PolicyDiscovery:
    """Result of a single pass over policy feature files."""

    catalog: PolicyCatalog
    feature_files: list[tuple[str, str]]
    api_requirements: ApiEnrichmentRequirements


def discover_policies(policy_roots: list[PolicyRoot | str]) -> PolicyDiscovery:
    """Walk policy dirs once: catalog metadata, file list, and API markers."""
    from src.compliance.api_enrichment import (
        ApiEnrichmentRequirements,
        update_requirements_from_text,
    )

    catalog = PolicyCatalog()
    feature_files: list[tuple[str, str]] = []
    api_requirements = ApiEnrichmentRequirements()
    seen_files: set[str] = set()

    for item in policy_roots:
        root = item if isinstance(item, PolicyRoot) else PolicyRoot(item)
        features_dir = root.path
        if not os.path.isdir(features_dir):
            raise FileNotFoundError(f"Features directory not found: {features_dir}")

        for feature_file in iter_feature_files(
            features_dir, sort_names=True, recursive=root.recursive
        ):
            real_path = os.path.realpath(feature_file)
            if real_path in seen_files:
                continue
            seen_files.add(real_path)
            with open(feature_file, encoding="utf-8") as handle:
                text = handle.read()
            catalog.features.append(parse_feature_policies(feature_file, text=text))
            feature_files.append((features_dir, feature_file))
            if not (
                api_requirements.enrich_includes
                and api_requirements.enrich_images
                and api_requirements.load_api_entities
            ):
                update_requirements_from_text(text, api_requirements)

    return PolicyDiscovery(
        catalog=catalog,
        feature_files=feature_files,
        api_requirements=api_requirements,
    )


def collect_policy_index(catalog: PolicyCatalog) -> list[PolicyAnnotation]:
    policies: list[PolicyAnnotation] = []
    for feature in catalog.features:
        if feature.annotation:
            policies.append(feature.annotation)
        policies.extend(feature.scenarios)
    return policies
