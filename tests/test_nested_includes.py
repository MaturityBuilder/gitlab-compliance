"""Prove deep local-include nesting for docs collection and compliance loading.

Uses tests/fixtures/nested-includes/ — a dual-branch tree with depth 4:

  .gitlab-ci.yml
  ├── includes/security.yml
  │   └── security/scanners.yml
  │       └── scanners/deep-sast.yml
  └── includes/build.yml
      └── build/docker.yml
          └── docker/publish.yml

Unit tests are preferred over a live CI workflow: they assert exact jobs,
include rows, and nested on/off behavior without needing a GitLab runner.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.compliance.model import load_yaml_entities
from src.compliance.runner import run_compliance
from src.modules.constants import (
    GITSTRINGS_MARKER_CLOSE,
    GITSTRINGS_MARKER_OPEN,
)
from src.modules.gitstrings import process_gitstrings
from src.modules.pipeline_data import collect_pipeline_data
from src.properties.table_render import render_includes_from_config

NESTED_ROOT = Path(__file__).resolve().parent / "fixtures" / "nested-includes"
NESTED_CI = NESTED_ROOT / ".gitlab-ci.yml"
NESTED_POLICIES = (
    Path(__file__).resolve().parent / "compliance_policies" / "nested-includes"
)
SHELL_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shell_check"

EXPECTED_NESTED_JOBS = {
    "root_lint",
    "security_gate",
    "secret_scan",
    "deep_sast",
    "compile",
    "docker_build",
    "publish_image",
}

EXPECTED_LOCAL_PATHS = {
    "includes/security.yml",
    "includes/build.yml",
    "security/scanners.yml",
    "scanners/deep-sast.yml",
    "build/docker.yml",
    "docker/publish.yml",
}

ROOT_ONLY_JOBS = {"root_lint"}
ROOT_ONLY_LOCAL_PATHS = {"includes/security.yml", "includes/build.yml"}

MARKER_BLOCK = f"""{GITSTRINGS_MARKER_OPEN}
{GITSTRINGS_MARKER_CLOSE}
"""


def _job_names(data: dict) -> set[str]:
    return {job["name"] for job in data["jobs"]}


def _local_include_paths(data: dict) -> set[str]:
    return {
        item["project"] for item in data["includes"] if item["include_type"] == "local"
    }


def _include_types(data: dict) -> set[str]:
    return {item["include_type"] for item in data["includes"]}


class TestNestedIncludeFixture:
    def test_fixture_tree_exists(self):
        assert NESTED_CI.is_file()
        assert (NESTED_ROOT / "includes/security/scanners/deep-sast.yml").is_file()
        assert (NESTED_ROOT / "includes/build/docker/publish.yml").is_file()


class TestCollectPipelineData:
    def test_include_nested_true_walks_full_tree(self):
        data = collect_pipeline_data(str(NESTED_CI), detailed=True, include_nested=True)

        assert _job_names(data) == EXPECTED_NESTED_JOBS
        assert EXPECTED_LOCAL_PATHS <= _local_include_paths(data)
        assert {
            "project",
            "component",
            "template",
            "remote",
            "local",
        } <= _include_types(data)

        project_files = {
            item["file"]
            for item in data["includes"]
            if item["include_type"] == "project"
        }
        assert "security/base.yml" in project_files
        assert "scanners.yml" in project_files

    def test_include_nested_false_keeps_only_root_entities(self):
        data = collect_pipeline_data(
            str(NESTED_CI), detailed=True, include_nested=False
        )

        assert _job_names(data) == ROOT_ONLY_JOBS
        assert _local_include_paths(data) == ROOT_ONLY_LOCAL_PATHS
        assert "deep_sast" not in _job_names(data)
        assert "publish_image" not in _job_names(data)

    def test_nested_jobs_preserve_source_files(self):
        data = collect_pipeline_data(str(NESTED_CI), detailed=True, include_nested=True)
        by_name = {job["name"]: job for job in data["jobs"]}

        assert by_name["root_lint"]["source_file"].endswith(".gitlab-ci.yml")
        assert by_name["deep_sast"]["source_file"].endswith("deep-sast.yml")
        assert by_name["publish_image"]["source_file"].endswith("publish.yml")

    def test_nested_container_images_are_collected(self):
        data = collect_pipeline_data(str(NESTED_CI), detailed=True, include_nested=True)
        images = {item["image"] for item in data["container_images"]}

        assert "registry.gitlab.com/security-products/sast:4.2.1" in images
        assert "docker:24.0.5" in images
        assert "python:3.12.0" in images

    def test_nested_variables_are_not_merged_today(self):
        """Document current collector limitation: only nested includes/jobs merge."""
        data = collect_pipeline_data(str(NESTED_CI), detailed=True, include_nested=True)
        variable_keys = {item["key"] for item in data["variables"]}

        assert "ROOT_VAR" in variable_keys
        assert "SECURITY_VAR" not in variable_keys
        assert "DEEP_SAST_VAR" not in variable_keys
        assert "PUBLISH_VAR" not in variable_keys

    def test_max_include_depth_none_matches_unlimited(self):
        unlimited = collect_pipeline_data(
            str(NESTED_CI), detailed=True, include_nested=True
        )
        limited = collect_pipeline_data(
            str(NESTED_CI),
            detailed=True,
            include_nested=True,
            max_include_depth=None,
        )
        assert _job_names(limited) == _job_names(unlimited) == EXPECTED_NESTED_JOBS

    def test_max_include_depth_zero_is_root_only(self):
        data = collect_pipeline_data(
            str(NESTED_CI),
            detailed=True,
            include_nested=True,
            max_include_depth=0,
        )
        assert _job_names(data) == ROOT_ONLY_JOBS
        assert "security_gate" not in _job_names(data)

    def test_max_include_depth_one_stops_after_first_hop(self):
        data = collect_pipeline_data(
            str(NESTED_CI),
            detailed=True,
            include_nested=True,
            max_include_depth=1,
        )
        jobs = _job_names(data)
        assert {"root_lint", "security_gate", "compile"} <= jobs
        assert "secret_scan" not in jobs
        assert "docker_build" not in jobs
        assert "deep_sast" not in jobs
        assert "publish_image" not in jobs

    def test_max_include_depth_two_includes_mid_level_not_leaves(self):
        data = collect_pipeline_data(
            str(NESTED_CI),
            detailed=True,
            include_nested=True,
            max_include_depth=2,
        )
        jobs = _job_names(data)
        assert {
            "root_lint",
            "security_gate",
            "compile",
            "secret_scan",
            "docker_build",
        } <= jobs
        assert "deep_sast" not in jobs
        assert "publish_image" not in jobs

    def test_diamond_include_is_visited_once(self, tmp_path):
        shared = tmp_path / "shared.yml"
        shared.write_text("shared_job:\n  script: [echo shared]\n", encoding="utf-8")
        left = tmp_path / "left.yml"
        left.write_text("include:\n  - local: shared.yml\n", encoding="utf-8")
        right = tmp_path / "right.yml"
        right.write_text("include:\n  - local: shared.yml\n", encoding="utf-8")
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n  - local: left.yml\n  - local: right.yml\n"
            "root_job:\n  script: [echo root]\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(root), detailed=True, include_nested=True)
        shared_jobs = [job for job in data["jobs"] if job["name"] == "shared_job"]
        assert len(shared_jobs) == 1

    def test_circular_include_does_not_recurse_forever(self, tmp_path):
        a = tmp_path / "a.yml"
        b = tmp_path / "b.yml"
        a.write_text(
            "include:\n  - local: b.yml\na_job:\n  script: [echo a]\n",
            encoding="utf-8",
        )
        b.write_text(
            "include:\n  - local: a.yml\nb_job:\n  script: [echo b]\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(a), detailed=True, include_nested=True)
        assert _job_names(data) == {"a_job", "b_job"}

    def test_missing_config_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            collect_pipeline_data(str(tmp_path / "missing.yml"))

    def test_local_include_outside_base_is_ignored(self, tmp_path):
        outside = tmp_path / "outside.yml"
        outside.write_text("evil:\n  script: [echo x]\n", encoding="utf-8")
        nested = tmp_path / "ci"
        nested.mkdir()
        root = nested / ".gitlab-ci.yml"
        root.write_text(
            "include:\n  - local: ../outside.yml\nroot:\n  script: [echo]\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(root), detailed=True, include_nested=True)
        assert _job_names(data) == {"root"}
        assert "evil" not in _job_names(data)

    def test_local_include_commonpath_error_is_ignored(self, tmp_path, monkeypatch):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n  - local: child.yml\nroot:\n  script: [echo]\n",
            encoding="utf-8",
        )
        (tmp_path / "child.yml").write_text(
            "child:\n  script: [echo]\n", encoding="utf-8"
        )
        monkeypatch.setattr(
            "src.modules.pipeline_data.os.path.commonpath",
            lambda _paths: (_ for _ in ()).throw(ValueError("cross-device")),
        )
        data = collect_pipeline_data(str(root), detailed=True, include_nested=True)
        assert _job_names(data) == {"root"}
        assert "child" not in _job_names(data)

    def test_yaml_index_failure_falls_back(self, tmp_path, monkeypatch):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text("job:\n  script: [echo]\n", encoding="utf-8")

        def boom(_text):
            raise RuntimeError("index failed")

        monkeypatch.setattr("src.modules.yaml_lines.index_yaml_text", boom)
        data = collect_pipeline_data(str(root), detailed=True, include_nested=False)
        assert _job_names(data) == {"job"}
        assert data["line_index"]["jobs"] == {}

    def test_run_compliance_respects_max_include_depth(self):
        result = run_compliance(
            features_dir=str(NESTED_POLICIES),
            pipeline_file=str(NESTED_CI),
            include_nested=True,
            max_include_depth=0,
            output_format="markdown",
        )
        assert result.success is True
        assert result.passed == 0
        assert result.skipped == 6


class TestIncludeResolutionReporting:
    def test_external_includes_recorded_when_not_resolved(self):
        data = collect_pipeline_data(str(NESTED_CI), detailed=True, include_nested=True)
        unresolved = data.get("unresolved_includes", [])
        reasons = {item["reason"] for item in unresolved}
        types = {item["include_type"] for item in unresolved}
        assert "project" in types
        assert "component" in types
        assert "template" in types
        assert "remote" in types
        assert "no_token" in reasons or "fetch_failed" in reasons

    def test_no_include_nested_records_local_gaps(self):
        data = collect_pipeline_data(
            str(NESTED_CI), detailed=True, include_nested=False
        )
        unresolved = data.get("unresolved_includes", [])
        assert unresolved
        assert all(item["reason"] == "include_nested_disabled" for item in unresolved)

    def test_max_depth_records_depth_exceeded(self):
        data = collect_pipeline_data(
            str(NESTED_CI),
            detailed=True,
            include_nested=True,
            max_include_depth=0,
        )
        unresolved = data.get("unresolved_includes", [])
        assert any(item["reason"] == "depth_exceeded" for item in unresolved)

    def test_remote_include_merged_when_fetch_succeeds(self, tmp_path):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n"
            "  - remote: https://example.com/ci.yml\n"
            "root:\n  script: [echo root]\n",
            encoding="utf-8",
        )
        with patch(
            "src.compliance.include_fetch.requests.get",
            return_value=MagicMock(
                status_code=200,
                text="remote_job:\n  script: [echo remote]\n",
            ),
        ) as mock_get:
            mock_get.return_value.raise_for_status = MagicMock()
            data = collect_pipeline_data(
                str(root),
                detailed=True,
                include_nested=True,
                resolve_external_includes=True,
            )
        assert "remote_job" in _job_names(data)
        assert not any(
            item["include_type"] == "remote" for item in data["unresolved_includes"]
        )

    def test_remote_nested_local_resolved_from_remote_base(self, tmp_path):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n"
            "  - remote: https://example.com/ci/root.yml\n"
            "root:\n  script: [echo root]\n",
            encoding="utf-8",
        )

        def _fake_get(url, headers=None, timeout=30):
            response = MagicMock(status_code=200)
            response.raise_for_status = MagicMock()
            if url.endswith("/ci/root.yml"):
                response.text = "include:\n  - local: nested.yml\nparent:\n  script: [echo parent]\n"
            elif url.endswith("/ci/nested.yml"):
                response.text = "nested:\n  script: [echo nested]\n"
            else:
                raise AssertionError(f"unexpected url {url}")
            return response

        with patch("src.compliance.include_fetch.requests.get", side_effect=_fake_get):
            data = collect_pipeline_data(
                str(root),
                detailed=True,
                include_nested=True,
                resolve_external_includes=True,
            )
        assert "nested" in _job_names(data)
        assert not data.get("unresolved_includes")

    def test_duplicate_remote_include_visited_once(self, tmp_path):
        root = tmp_path / ".gitlab-ci.yml"
        root.write_text(
            "include:\n"
            "  - remote: https://example.com/shared.yml\n"
            "  - remote: https://example.com/shared.yml\n"
            "root:\n  script: [echo root]\n",
            encoding="utf-8",
        )
        with patch(
            "src.compliance.include_fetch.requests.get",
            return_value=MagicMock(
                status_code=200,
                text="shared:\n  script: [echo shared]\n",
            ),
        ) as mock_get:
            mock_get.return_value.raise_for_status = MagicMock()
            data = collect_pipeline_data(
                str(root),
                detailed=True,
                include_nested=True,
                resolve_external_includes=True,
            )
        assert sum(1 for job in data["jobs"] if job["name"] == "shared") == 1
        assert mock_get.call_count == 1

    def test_duplicate_job_names_keep_distinct_scripts(self):
        from src.compliance.script_analysis import script_has_unpinned_apt

        data = collect_pipeline_data(
            str(SHELL_FIXTURES / "collision-root.yml"),
            include_nested=True,
            resolve_job_composition=True,
        )
        jobs = {(job["name"], job["source_file"]): job for job in data["jobs"]}
        child_key = next(
            key
            for key in jobs
            if key[0] == "a" and key[1].endswith("collision-child.yml")
        )
        root_key = next(
            key
            for key in jobs
            if key[0] == "a" and key[1].endswith("collision-root.yml")
        )
        child_entity = {
            "name": "a",
            "effective_script": jobs[child_key]["effective_script"],
        }
        root_entity = {
            "name": "a",
            "effective_script": jobs[root_key]["effective_script"],
        }
        assert script_has_unpinned_apt(child_entity)
        assert not script_has_unpinned_apt(root_entity)


class TestComplianceNestedLoading:
    def test_load_yaml_entities_nested_true(self):
        entities, unresolved = load_yaml_entities(str(NESTED_CI), include_nested=True)
        job_names = {job["name"] for job in entities["jobs"]}
        include_projects = {
            include["values"].get("project") for include in entities["includes"]
        }

        assert job_names == EXPECTED_NESTED_JOBS
        assert EXPECTED_LOCAL_PATHS <= include_projects
        assert any(
            image["values"]["image"]
            == "registry.gitlab.com/security-products/sast:4.2.1"
            for image in entities["container_images"]
        )
        assert unresolved

    def test_load_yaml_entities_nested_false(self):
        entities, unresolved = load_yaml_entities(str(NESTED_CI), include_nested=False)
        job_names = {job["name"] for job in entities["jobs"]}

        assert job_names == ROOT_ONLY_JOBS
        assert "deep_sast" not in job_names
        assert unresolved

    def test_check_workflow_passes_with_nested_enabled(self):
        result = run_compliance(
            features_dir=str(NESTED_POLICIES),
            pipeline_file=str(NESTED_CI),
            include_nested=True,
            output_format="markdown",
        )
        assert result.success is True
        assert result.passed == 6
        assert result.skipped == 0
        assert result.failed == 0

    def test_check_workflow_skips_leaf_jobs_without_nested(self):
        result = run_compliance(
            features_dir=str(NESTED_POLICIES),
            pipeline_file=str(NESTED_CI),
            include_nested=False,
            output_format="markdown",
        )
        # Missing named jobs skip rather than fail; proves nesting was required.
        assert result.success is True
        assert result.passed == 0
        assert result.skipped == 6


class TestGitstringsNestedDocs:
    def test_render_includes_lists_deep_locals_when_nested(self):
        markdown = render_includes_from_config(str(NESTED_CI), include_nested=True)
        for path in EXPECTED_LOCAL_PATHS:
            assert path in markdown
        assert "deep-sast.yml" in markdown
        assert "publish.yml" in markdown

    def test_render_includes_omits_deep_locals_when_shallow(self):
        markdown = render_includes_from_config(str(NESTED_CI), include_nested=False)
        assert "includes/security.yml" in markdown
        assert "includes/build.yml" in markdown
        assert "deep-sast.yml" not in markdown
        assert "publish.yml" not in markdown

    def test_process_gitstrings_include_nested_flag(self, tmp_path):
        tree = tmp_path / "nested"
        shutil.copytree(NESTED_ROOT, tree)
        ci = tree / ".gitlab-ci.yml"
        ci.write_text(
            "# @title Nested includes\n"
            "# @render includes\n" + ci.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        readme = tmp_path / "README.md"
        readme.write_text(MARKER_BLOCK, encoding="utf-8")

        process_gitstrings(ci, readme, keep_source=False, include_nested=False)
        shallow = readme.read_text(encoding="utf-8")
        assert "includes/security.yml" in shallow
        assert "deep-sast.yml" not in shallow
        assert "publish.yml" not in shallow

        process_gitstrings(ci, readme, keep_source=False, include_nested=True)
        nested = readme.read_text(encoding="utf-8")
        assert "includes/security.yml" in nested
        assert "deep-sast.yml" in nested
        assert "publish.yml" in nested
