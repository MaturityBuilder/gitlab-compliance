from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.compliance.api_config import (
    group_api_ready,
    project_api_ready,
    require_api_connection,
    resolve_group,
    resolve_project,
    resolve_token,
)
from src.compliance.metadata import (
    PolicyCatalog,
    build_policy_catalog,
    parse_feature_policies,
)
from src.compliance.model import load_pipeline_entities, load_yaml_entities
from src.compliance.policy_doc import render_policy_catalog
from src.compliance.stash import (
    assert_all,
    entity_has_property,
    extends_includes,
    filter_entities,
    format_entity_ref,
    get_property,
    name_starts_with,
    normalize_value,
    property_matches,
    property_matches_regex,
    property_not_matches_regex,
)
from src.compliance.console import render_compliance_console
from src.compliance.models import ComplianceResult, ScenarioResult

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"
ANNOTATED = REPO_ROOT / "tests" / "compliance_policies" / "annotated"


class TestStash:
    def test_normalize_and_property_helpers(self):
        assert normalize_value(None) == ""
        assert normalize_value(True) == "true"

        entity = {
            "name": "build",
            "values": {"stage": "test", "image": {"name": "docker:24"}},
            "source_file": "/proj/.gitlab-ci.yml",
            "line": 10,
        }
        assert get_property(entity, "stage") == "test"
        assert get_property(entity, "image") == "docker:24"
        assert entity_has_property(entity, "stage")
        assert property_matches(entity, "stage", "test")
        assert property_matches_regex(entity, "image", r"docker")
        assert property_not_matches_regex(entity, "image", r"latest")
        assert name_starts_with(entity, "bu")
        assert extends_includes({**entity, "extends": "template"}, "template")
        assert extends_includes({**entity, "extends": ["template"]}, "template")
        assert not extends_includes(entity, "missing")
        assert "build" in format_entity_ref(entity)
        assert filter_entities([entity], lambda e: True) == [entity]
        assert_all([entity], lambda e: True, "ok")

    def test_invalid_regex_raises(self):
        with pytest.raises(ValueError, match="Invalid regex"):
            property_matches_regex({"values": {"x": "1"}}, "x", "(")


class TestApiConfig:
    def test_resolve_and_ready(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "tok")
        monkeypatch.setenv("CI_PROJECT_PATH", "g/p")
        assert resolve_token({}) == "tok"
        assert resolve_project({}) == "g/p"
        assert project_api_ready({})
        monkeypatch.setenv("GITLAB_GROUP_PATH", "my-group")
        assert resolve_group({}) == "my-group"
        assert group_api_ready({})

    def test_require_api_connection_skips(self):
        context = SimpleNamespace(
            config=SimpleNamespace(userdata={"strict": "false"}),
            scenario=SimpleNamespace(skip=MagicMock()),
            scenario_skipped=False,
        )
        assert require_api_connection(context, "project", "label") is False
        context.scenario.skip.assert_called_once()

    def test_require_api_connection_strict_raises(self):
        context = SimpleNamespace(
            config=SimpleNamespace(userdata={"strict": "true"}),
            scenario=SimpleNamespace(skip=MagicMock()),
            scenario_skipped=False,
        )
        with pytest.raises(AssertionError, match="GitLab API connection"):
            require_api_connection(context, "group", "label")


class TestMetadataAndPolicyDoc:
    def test_build_catalog_from_annotated(self):
        catalog = build_policy_catalog(str(ANNOTATED))
        assert catalog.features
        feature = catalog.features[0]
        assert feature.feature_name

    def test_lookup_scenario(self):
        catalog = build_policy_catalog(str(ANNOTATED))
        feature_file = catalog.features[0].feature_file
        if catalog.features[0].scenarios:
            name = catalog.features[0].scenarios[0].scenario_name
            assert catalog.lookup_scenario(feature_file, name) is not None

    def test_parse_non_dict_metadata(self, tmp_path):
        feature = tmp_path / "meta.feature"
        feature.write_text(
            "# METADATA\n# just-a-string\nFeature: Meta\n  Scenario: S\n    Given x\n",
            encoding="utf-8",
        )
        parsed = parse_feature_policies(str(feature))
        assert parsed.feature_name == "Meta"

    def test_parse_minimal_feature(self, tmp_path):
        feature = tmp_path / "minimal.feature"
        feature.write_text("Feature: Minimal\n  Scenario: One\n    Given x\n", encoding="utf-8")
        parsed = parse_feature_policies(str(feature))
        assert parsed.feature_name == "Minimal"

    def test_build_catalog_missing_dir(self):
        with pytest.raises(FileNotFoundError):
            build_policy_catalog("/no/such/policies")

    def test_render_policy_catalog_html(self):
        catalog = build_policy_catalog(str(ANNOTATED))
        html = render_policy_catalog(catalog, str(ANNOTATED), "html")
        assert "<html" in html.lower()


class TestModel:
    def test_load_yaml_entities_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_yaml_entities("/missing.yml")

    def test_load_pipeline_entities_with_api_mock(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "t")
        monkeypatch.setenv("CI_PROJECT_PATH", "g/p")
        api_payload = {
            "project_settings": [{"name": "x"}],
            "project_ci_variables": [],
            "group_settings": [],
        }
        with patch("src.compliance.gitlab_api.load_api_entities", return_value=api_payload):
            entities = load_pipeline_entities(str(SAMPLE), token="t", project="g/p")
        assert entities["project_settings"]


class TestConsole:
    def test_render_compliance_console(self, capsys):
        result = ComplianceResult(
            success=False,
            exit_code=1,
            scenario_results=[
                ScenarioResult(
                    feature="f.feature",
                    name="n",
                    status="failed",
                    message="oops",
                )
            ],
            scenarios=1,
            passed=0,
            failed=1,
            skipped=0,
        )
        render_compliance_console(result, str(SAMPLE), str(ANNOTATED))
        assert capsys.readouterr().out
