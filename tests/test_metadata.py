"""Tests for compliance policy METADATA parsing."""

from pathlib import Path

from src.compliance.metadata import (
    _parse_metadata_yaml,
    build_policy_catalog,
    normalize_scenario_name,
    parse_feature_policies,
)

EXAMPLE_POLICIES = Path(__file__).resolve().parents[1] / "examples/example-policies"
OUTLINE_POLICIES = (
    Path(__file__).resolve().parents[1] / "tests/compliance_policies/outlines"
)


class TestParseMetadataYaml:
    def test_description_with_when_colon(self):
        yaml_lines = [
            "title: Rules must include conditional guards",
            "description: Jobs with rules must use if/when guards, not only when: always.",
            "custom:",
            "  id: GLCI-EXECUTION-POLICY-002",
            "  severity: MEDIUM",
        ]
        parsed = _parse_metadata_yaml(yaml_lines)
        assert parsed["title"] == "Rules must include conditional guards"
        assert "when: always" in parsed["description"]
        assert parsed["custom"]["id"] == "GLCI-EXECUTION-POLICY-002"
        assert parsed["custom"]["severity"] == "MEDIUM"

    def test_description_with_image_colon(self):
        yaml_lines = [
            "title: No mutable latest tags",
            "description: Prevents jobs from using mutable latest tags such as docker:latest.",
        ]
        parsed = _parse_metadata_yaml(yaml_lines)
        assert "docker:latest" in parsed["description"]

    def test_already_quoted_description_unchanged(self):
        yaml_lines = [
            'description: "Jobs with rules must use if/when guards, not only when: always."',
        ]
        parsed = _parse_metadata_yaml(yaml_lines)
        assert parsed["description"] == (
            "Jobs with rules must use if/when guards, not only when: always."
        )


class TestParseFeaturePolicies:
    def test_execution_policy_scenario_metadata(self):
        feature_file = EXAMPLE_POLICIES / "security" / "execution-policy.feature"
        policies = parse_feature_policies(str(feature_file))
        scenario = next(
            s
            for s in policies.scenarios
            if s.scenario_name == "Jobs with rules must include conditional guards"
        )
        assert scenario.policy_id == "GLCI-EXECUTION-POLICY-002"
        assert "when: always" in scenario.description


class TestBuildPolicyCatalog:
    def test_example_policies_load_without_yaml_error(self):
        catalog = build_policy_catalog(str(EXAMPLE_POLICIES))
        assert len(catalog.features) > 0


class TestScenarioOutlineMetadata:
    def test_outline_scenario_indexed(self):
        feature_file = OUTLINE_POLICIES / "metadata-outline.feature"
        policies = parse_feature_policies(str(feature_file))
        scenario = next(
            s
            for s in policies.scenarios
            if s.scenario_name == "Variables must match pattern"
        )
        assert scenario.policy_id == "GLCI-OUTLINE-TEST-001"
        assert scenario.scope == "scenario"

    def test_normalize_scenario_name_strips_behave_suffix(self):
        expanded = "Variables must match pattern -- @1.1"
        assert normalize_scenario_name(expanded) == "Variables must match pattern"

    def test_lookup_scenario_with_behave_outline_suffix(self):
        feature_file = OUTLINE_POLICIES / "metadata-outline.feature"
        catalog = build_policy_catalog(str(OUTLINE_POLICIES))
        annotation = catalog.lookup_scenario(
            str(feature_file), "Variables must match pattern -- @1.1"
        )
        assert annotation is not None
        assert annotation.policy_id == "GLCI-OUTLINE-TEST-001"
        assert annotation.scenario_name == "Variables must match pattern"
