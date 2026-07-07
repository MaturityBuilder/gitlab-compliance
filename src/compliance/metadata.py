"""Parse Conftest-style # METADATA annotations from compliance policy files."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

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
        for feature in self.features:
            if os.path.realpath(feature.feature_file) != normalized:
                continue
            for scenario in feature.scenarios:
                if scenario.scenario_name == scenario_name:
                    return scenario
        return None


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


def parse_feature_policies(feature_file: str) -> FeaturePolicies:
    feature_path = os.path.realpath(feature_file)
    with open(feature_path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

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
        if stripped.startswith("Scenario:"):
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
    catalog = PolicyCatalog()
    if not os.path.isdir(features_dir):
        raise FileNotFoundError(f"Features directory not found: {features_dir}")

    feature_files: list[str] = []
    for root, _dirs, files in os.walk(features_dir):
        for filename in sorted(files):
            if filename.endswith(".feature"):
                feature_files.append(os.path.join(root, filename))

    for feature_file in feature_files:
        catalog.features.append(parse_feature_policies(feature_file))

    return catalog


def collect_policy_index(catalog: PolicyCatalog) -> list[PolicyAnnotation]:
    policies: list[PolicyAnnotation] = []
    for feature in catalog.features:
        if feature.annotation:
            policies.append(feature.annotation)
        policies.extend(feature.scenarios)
    return policies
