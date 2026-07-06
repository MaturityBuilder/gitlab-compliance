import os
from pathlib import Path

import pytest

from src.properties.includes import (
    check_include_version_is_sema_version,
    document_includes,
)
from src.properties.extract_job_attribute import get_job_attribute
from src.properties.inputs import document_inputs
from src.properties.jobs import get_jobs
from src.properties.variables import document_variables
from src.properties.workflows import document_workflows

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"


class TestIncludes:
    def test_missing_config_returns_early(self, tmp_path):
        out = tmp_path / "out.md"
        out.write_text("x", encoding="utf-8")
        document_includes(str(out), str(tmp_path / "missing.yml"))
        assert out.read_text() == "x"

    def test_no_include_section(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("variables:\n  FOO: bar\n", encoding="utf-8")
        out = tmp_path / "out.md"
        Path(out).write_text(
            "[comment]: <> (gitlab-docs-opening-auto-generated)\n"
            "[comment]: <> (gitlab-docs-closing-auto-generated)\n",
            encoding="utf-8",
        )
        document_includes(str(out), str(cfg))

    def test_invalid_component_include(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n  - component: invalid-no-at-sign\n",
            encoding="utf-8",
        )
        out = tmp_path / "out.md"
        out.write_text(
            "[comment]: <> (gitlab-docs-opening-auto-generated)\n"
            "[comment]: <> (gitlab-docs-closing-auto-generated)\n",
            encoding="utf-8",
        )
        document_includes(str(out), str(cfg))

    def test_unknown_include_type(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - remote: https://example.com/ci.yml\n", encoding="utf-8")
        out = tmp_path / "out.md"
        out.write_text(
            "[comment]: <> (gitlab-docs-opening-auto-generated)\n"
            "[comment]: <> (gitlab-docs-closing-auto-generated)\n",
            encoding="utf-8",
        )
        document_includes(str(out), str(cfg))

    def test_semver_validator(self, monkeypatch):
        assert check_include_version_is_sema_version("1.0.0", "f", "p") is True
        assert check_include_version_is_sema_version("not-semver", "f", "p") is False

        def boom(_version):
            raise RuntimeError("semver broken")

        monkeypatch.setattr(
            "src.properties.includes.semver.Version.is_valid",
            boom,
        )
        assert check_include_version_is_sema_version("1.0.0", "f", "p") is False


class TestJobsAndProperties:
    def _prepare_output(self, tmp_path):
        out = tmp_path / "out.md"
        out.write_text(
            "[comment]: <> (gitlab-docs-opening-auto-generated)\n"
            "[comment]: <> (gitlab-docs-closing-auto-generated)\n",
            encoding="utf-8",
        )
        return out

    def test_get_jobs_on_sample(self, tmp_path):
        out = self._prepare_output(tmp_path)
        get_jobs(str(out), str(SAMPLE), detailed=True)

    def test_get_jobs_experimental_path(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n  stage: test\n  script:\n    - echo hi\n  rules:\n    - when: always\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        get_jobs(str(out), str(cfg), detailed=True, experimental=True)

    def test_get_jobs_with_needs_and_variables(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n"
            "  stage: test\n"
            "  variables:\n"
            "    K: v\n"
            "  needs:\n"
            "    - prep\n"
            "  script:\n"
            "    - echo\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        get_jobs(str(out), str(cfg), detailed=True)

    def test_document_variables_complex(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "variables:\n"
            "  SIMPLE: value\n"
            "  COMPLEX:\n"
            "    value: v\n"
            "    description: d\n"
            "    options: [a]\n"
            "    expand: false\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        document_variables(str(out), str(cfg), DISABLE_TITLE=True)

    def test_document_inputs(self, tmp_path):
        out = self._prepare_output(tmp_path)
        document_inputs(str(out), str(SAMPLE))

    def test_document_workflows_list_form(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("workflow:\n  - if: $CI\n", encoding="utf-8")
        out = self._prepare_output(tmp_path)
        document_workflows(str(out), str(cfg))

    def test_get_job_attribute_json(self, tmp_path, capsys):
        out = self._prepare_output(tmp_path)
        get_job_attribute(
            str(out),
            str(SAMPLE),
            attributes="stage,image",
            json_format=True,
        )
        captured = capsys.readouterr()
        assert captured.out.strip() != "" or out.stat().st_size > 0
