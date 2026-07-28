"""Tests for pipeline include and container image parsing."""

from pathlib import Path

from src.modules.pipeline_data import (
    _iter_include_entries,
    _parse_include_entry,
    _parse_remote_url_version,
    collect_pipeline_data,
)

SHELL_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shell_check"

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "includes-all-types.yml"
)


class TestParseRemoteUrlVersion:
    def test_extracts_semver_from_gitlab_raw_url(self):
        url = "https://gitlab.com/group/proj/-/raw/2.1.0/ci/template.yml"
        assert _parse_remote_url_version(url) == "2.1.0"


class TestParseIncludeEntry:
    def test_parses_template_include(self):
        parsed = _parse_include_entry({"template": "Auto-DevOps.gitlab-ci.yml"}, line=3)
        assert parsed["include_type"] == "template"
        assert parsed["valid_version"] is False

    def test_parses_remote_include(self):
        parsed = _parse_include_entry(
            {"remote": "https://gitlab.com/group/proj/-/raw/2.1.0/ci/template.yml"},
            line=4,
        )
        assert parsed["include_type"] == "remote"
        assert parsed["version"] == "2.1.0"
        assert parsed["valid_version"] is True

    def test_parses_component_include(self):
        parsed = _parse_include_entry(
            {"component": "gitlab.com/org/pipeline@1.2.0"},
            line=5,
        )
        assert parsed["include_type"] == "component"
        assert parsed["version"] == "1.2.0"


class TestIterIncludeEntries:
    def test_string_include_becomes_single_entry(self):
        assert _iter_include_entries("ci/child.yml") == ["ci/child.yml"]

    def test_dict_include_becomes_single_entry(self):
        spec = {"local": "ci/child.yml"}
        assert _iter_include_entries(spec) == [spec]

    def test_list_include_is_unchanged(self):
        entries = [{"local": "a.yml"}, "b.yml"]
        assert _iter_include_entries(entries) == entries


class TestCollectPipelineData:
    def test_unresolved_includes_recorded_for_external_entries(self):
        data = collect_pipeline_data(str(FIXTURE), detailed=True, include_nested=True)
        unresolved = data.get("unresolved_includes", [])
        assert unresolved
        assert {item["include_type"] for item in unresolved} >= {
            "project",
            "remote",
            "component",
            "template",
        }

    def test_resolve_external_disabled_skips_remote_fetch(self, tmp_path):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n  - remote: https://example.com/ci.yml\n"
            "job:\n  script: [echo]\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(
            str(root),
            detailed=True,
            include_nested=True,
            resolve_external_includes=False,
        )
        assert any(
            item["reason"] == "external_resolution_disabled"
            for item in data["unresolved_includes"]
        )

    def test_collects_all_include_types_and_container_images(self):
        data = collect_pipeline_data(str(FIXTURE), detailed=True)
        include_types = {item["include_type"] for item in data["includes"]}
        assert include_types >= {"project", "component", "template", "remote", "local"}
        assert len(data["container_images"]) >= 2
        job_images = [
            image
            for image in data["container_images"]
            if image["image_source"] == "job"
        ]
        assert any(image["image"] == "python:3.12.0" for image in job_images)

    def test_exclude_variables_and_group_by_stage(self):
        data = collect_pipeline_data(
            str(FIXTURE),
            detailed=True,
            exclude_sections={"variables"},
            exclude_attributes={"image"},
            group_by="stage",
        )
        assert data["variables"] == []
        assert data["group_by"] == "stage"
        assert data["jobs_grouped"]
        for job in data["jobs"]:
            assert all(item["key"] != "image" for item in job["attributes"])

    def test_string_include_loads_nested_jobs(self):
        data = collect_pipeline_data(
            str(SHELL_FIXTURES / "string-include.yml"),
            include_nested=True,
            resolve_job_composition=True,
        )
        names = {job["name"] for job in data["jobs"]}
        assert ".template" in names
        assert "deploy" in names

    def test_dict_include_loads_nested_jobs(self):
        data = collect_pipeline_data(
            str(SHELL_FIXTURES / "dict-include.yml"),
            include_nested=True,
            resolve_job_composition=True,
        )
        names = {job["name"] for job in data["jobs"]}
        assert ".template" in names
        assert "deploy" in names
