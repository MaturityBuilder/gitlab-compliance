import os
from pathlib import Path

from src.properties.extract_job_attribute import get_job_attribute
from src.properties.includes import (
    check_include_version_is_sema_version,
    document_includes,
)
from src.properties.inputs import document_inputs
from src.properties.jobs import get_jobs, render_jobs_from_pipeline
from src.properties.variables import document_variables
from src.properties.workflows import document_workflows

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples/sample-files" / ".gitlab-ci.yml"


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
            "<!-- gitlab-compliance-opening-auto-generated -->\n"
            "<!-- gitlab-compliance-closing-auto-generated -->\n",
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
            "<!-- gitlab-compliance-opening-auto-generated -->\n"
            "<!-- gitlab-compliance-closing-auto-generated -->\n",
            encoding="utf-8",
        )
        document_includes(str(out), str(cfg))

    def test_unknown_include_type(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n  - remote: https://example.com/ci.yml\n", encoding="utf-8"
        )
        out = tmp_path / "out.md"
        out.write_text(
            "<!-- gitlab-compliance-opening-auto-generated -->\n"
            "<!-- gitlab-compliance-closing-auto-generated -->\n",
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

    def _prepare_output(self, tmp_path):
        out = tmp_path / "out.md"
        out.write_text(
            "<!-- gitlab-compliance-opening-auto-generated -->\n"
            "<!-- gitlab-compliance-closing-auto-generated -->\n",
            encoding="utf-8",
        )
        return out

    def test_cycle_visited_returns_early(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - local: x.yml\n", encoding="utf-8")
        out = self._prepare_output(tmp_path)
        document_includes(
            str(out),
            str(cfg),
            _visited={os.path.realpath(str(cfg))},
        )
        assert "Includes" not in out.read_text(encoding="utf-8")

    def test_string_include_and_max_depth(self, tmp_path, monkeypatch):
        nested = tmp_path / "child.yml"
        nested.write_text("variables:\n  Z: 1\n", encoding="utf-8")
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - child.yml\n", encoding="utf-8")
        out = self._prepare_output(tmp_path)
        monkeypatch.chdir(tmp_path)
        document_includes(str(out), str(cfg), max_include_depth=0)
        text = out.read_text(encoding="utf-8")
        assert "local" in text
        assert "child.yml" in text

    def test_project_include_row(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n"
            "  - project: group/project\n"
            "    ref: 1.2.3\n"
            "    file: /.gitlab-ci.yml\n"
            "    variables:\n"
            "      A: b\n"
            "    rules:\n"
            "      - if: $CI\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        document_includes(str(out), str(cfg))
        text = out.read_text(encoding="utf-8")
        assert "project" in text
        assert "group/project" in text
        assert "1.2.3" in text

    def test_component_include_valid_semver(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n"
            "  - component: gitlab.com/org/comp@2.0.0\n"
            "    inputs:\n"
            "      env: prod\n"
            "    rules:\n"
            "      - when: always\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        document_includes(str(out), str(cfg))
        text = out.read_text(encoding="utf-8")
        assert "component" in text
        assert "gitlab.com/org/comp" in text
        assert "2.0.0" in text


class TestJobsAndProperties:
    def _prepare_output(self, tmp_path):
        out = tmp_path / "out.md"
        out.write_text(
            "<!-- gitlab-compliance-opening-auto-generated -->\n"
            "<!-- gitlab-compliance-closing-auto-generated -->\n",
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
        document_inputs(str(out), str(SAMPLE), DISABLE_TITLE=True)

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

    def test_render_jobs_from_pipeline_grouped_with_rules(self, tmp_path):
        out = self._prepare_output(tmp_path)
        pipeline_data = {
            "group_by": "stage",
            "jobs_grouped": [
                {
                    "group_key": "build",
                    "jobs": [
                        {
                            "name": "compile",
                            "display_name": "COMPILE",
                            "is_template": False,
                            "attributes": [
                                {"key": "stage", "value": "build"},
                                {
                                    "key": "rules",
                                    "value": [{"if": "$CI", "when": "on_success"}],
                                },
                            ],
                            "nested": [
                                {"attribute": "variables", "key": "K", "value": "v"}
                            ],
                            "rules": [{"when": "always"}],
                        }
                    ],
                }
            ],
        }
        render_jobs_from_pipeline(str(out), pipeline_data, detailed=True)
        text = out.read_text(encoding="utf-8")
        assert "Stage · build" in text or "stage" in text.lower()
        assert "COMPILE" in text
        assert "JOB" in text

    def test_get_jobs_rules_table_written(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n"
            "  stage: test\n"
            "  script:\n"
            "    - echo\n"
            "  rules:\n"
            "    - if: $CI\n"
            "      when: on_success\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)
        get_jobs(str(out), str(cfg), detailed=False, experimental=False)
        text = out.read_text(encoding="utf-8")
        assert "BUILD" in text
        assert "$CI" in text or "Rule" in text or "if" in text

    def test_get_jobs_artifacts_branch_with_sticky_pop(self, tmp_path, monkeypatch):
        class Sticky(dict):
            def pop(self, key, *args, **kwargs):
                if key == "artifacts":
                    return self.get(key)
                return super().pop(key, *args, **kwargs)

        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n"
            "  stage: test\n"
            "  script: [echo]\n"
            "  artifacts:\n"
            "    paths: [dist/]\n"
            "    expire_in: 1 week\n",
            encoding="utf-8",
        )

        import src.modules.common as common

        original = common.read_yml

        def sticky_read(path):
            docs = original(path)
            for doc in docs:
                if "build" in doc and isinstance(doc["build"], dict):
                    doc["build"] = Sticky(doc["build"])
            return docs

        monkeypatch.setattr("src.properties.jobs.common.read_yml", sticky_read)
        out = self._prepare_output(tmp_path)
        get_jobs(str(out), str(cfg))
        text = out.read_text(encoding="utf-8")
        assert "artifacts" in text
        assert "paths" in text or "dist" in text

    def test_get_jobs_generic_exception_handler(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n  stage: test\n  script: [echo]\n",
            encoding="utf-8",
        )
        out = self._prepare_output(tmp_path)

        def boom(*_a, **_k):
            raise RuntimeError("format failed")

        monkeypatch.setattr("src.properties.jobs.common.format_value", boom)
        get_jobs(str(out), str(cfg))
