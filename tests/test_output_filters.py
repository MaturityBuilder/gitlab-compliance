"""Tests for generate output filtering and grouping."""

from src.modules.output_filters import (
    UNSET_GROUP_KEY,
    apply_output_filters,
    filter_job,
    group_jobs,
    parse_exclude,
    validate_exclude_sections,
)


def _sample_job(name="build", stage="test", image="python:3.12"):
    return {
        "name": name,
        "display_name": name.upper(),
        "is_template": False,
        "attributes": [
            {"key": "stage", "value": stage},
            {"key": "image", "value": image},
        ],
        "rules": [{"if": "$CI"}],
        "nested": [{"attribute": "variables", "key": "FOO", "value": "bar"}],
    }


class TestParseExclude:
    def test_splits_sections_and_attributes(self):
        sections, attrs = parse_exclude("variables,workflow,image,stage")
        assert sections == {"variables", "workflow"}
        assert attrs == {"image", "stage"}

    def test_empty_exclude(self):
        sections, attrs = parse_exclude(None)
        assert sections == set()
        assert attrs == set()


class TestValidateExcludeSections:
    def test_rejects_unknown_section(self):
        try:
            validate_exclude_sections({"bogus"})
            assert False, "expected ValueError"
        except ValueError as exc:
            assert "Unknown section" in str(exc)


class TestFilterJob:
    def test_removes_attributes_rules_and_nested(self):
        job = _sample_job()
        filtered = filter_job(job, {"image", "rules", "variables"})
        keys = {item["key"] for item in filtered["attributes"]}
        assert "image" not in keys
        assert "stage" in keys
        assert filtered["rules"] == []
        assert filtered["nested"] == []


class TestGroupJobs:
    def test_groups_by_stage(self):
        jobs = [
            _sample_job("a", stage="build"),
            _sample_job("b", stage="test"),
            _sample_job("c", stage="build"),
        ]
        grouped = group_jobs(jobs, "stage")
        assert len(grouped) == 2
        assert grouped[0]["group_key"] == "build"
        assert len(grouped[0]["jobs"]) == 2
        assert grouped[1]["group_key"] == "test"

    def test_missing_attribute_goes_to_unset(self):
        job = {
            "name": "x",
            "attributes": [],
            "rules": [],
            "nested": [],
        }
        grouped = group_jobs([job], "stage")
        assert grouped[0]["group_key"] == UNSET_GROUP_KEY

    def test_no_group_by_returns_single_block(self):
        jobs = [_sample_job()]
        grouped = group_jobs(jobs, None)
        assert len(grouped) == 1
        assert grouped[0]["group_key"] == ""


class TestApplyOutputFilters:
    def test_excludes_variables_section(self):
        data = {
            "inputs": [{"key": "x"}],
            "variables": [{"key": "y"}],
            "includes": [],
            "workflow_rules": [],
            "jobs": [_sample_job()],
            "container_images": [],
        }
        result = apply_output_filters(data, exclude_sections={"variables"})
        assert result["variables"] == []
        assert result["jobs_grouped"]

    def test_excludes_jobs_section(self):
        data = {
            "inputs": [],
            "variables": [],
            "includes": [],
            "workflow_rules": [],
            "jobs": [_sample_job()],
            "container_images": [{"image": "x"}],
        }
        result = apply_output_filters(data, exclude_sections={"jobs"})
        assert result["jobs"] == []
        assert result["jobs_grouped"] == []
