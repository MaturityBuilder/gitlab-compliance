# nosec
import os
import tempfile

import pytest

from src.compliance.stash import property_matches_regex
from src.modules.pipeline_data import collect_pipeline_data


class TestLocalIncludePathSafety:
    def test_rejects_path_outside_project_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "project")
            os.makedirs(root)
            main_ci = os.path.join(root, ".gitlab-ci.yml")
            with open(main_ci, "w", encoding="utf-8") as handle:
                handle.write(
                    "include:\n"
                    "  - local: ../outside.yml\n"
                    "job:\n"
                    "  script:\n"
                    "    - echo hi\n"
                )
            outside = os.path.join(tmp, "outside.yml")
            with open(outside, "w", encoding="utf-8") as handle:
                handle.write("outside_job:\n  script:\n    - echo no\n")

            data = collect_pipeline_data(main_ci, detailed=True, include_nested=True)
            job_names = {job["name"] for job in data["jobs"]}
            assert "outside_job" not in job_names

    def test_resolves_nested_local_include_relative_to_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested_dir = os.path.join(tmp, "ci")
            os.makedirs(nested_dir)
            nested_ci = os.path.join(nested_dir, "child.yml")
            with open(nested_ci, "w", encoding="utf-8") as handle:
                handle.write("child_job:\n  script:\n    - echo child\n")
            main_ci = os.path.join(tmp, ".gitlab-ci.yml")
            with open(main_ci, "w", encoding="utf-8") as handle:
                handle.write(
                    "include:\n"
                    "  - local: ci/child.yml\n"
                    "root_job:\n"
                    "  script:\n"
                    "    - echo root\n"
                )

            data = collect_pipeline_data(main_ci, detailed=True, include_nested=True)
            job_names = {job["name"] for job in data["jobs"]}
            assert "child_job" in job_names
            assert "root_job" in job_names


class TestRegexMatching:
    def test_invalid_pattern_raises_clear_error(self):
        entity = {"values": {"image": "alpine:latest"}}
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            property_matches_regex(entity, "image", "(")
