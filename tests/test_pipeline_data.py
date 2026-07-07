"""Tests for pipeline include and container image parsing."""

from pathlib import Path

from src.modules.pipeline_data import (
    _parse_include_entry,
    _parse_remote_url_version,
    collect_pipeline_data,
)

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


class TestCollectPipelineData:
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
