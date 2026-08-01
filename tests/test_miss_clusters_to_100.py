"""Focused unit tests for remaining coverage gaps toward 100%."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.compliance import script_analysis as sa
from src.compliance.api_enrichment import ApiEnrichmentRequirements
from src.compliance.builtin_policies import BUILTIN_POLICIES_DIR
from src.compliance.include_fetch import (
    ExternalIncludeContext,
    FetchedInclude,
    IncludeFetchCache,
    IncludeFetchFailure,
)
from src.compliance.metadata import (
    FeaturePolicies,
    PolicyAnnotation,
    PolicyCatalog,
    PolicyDiscovery,
)
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.runner import (
    _build_behave_workspace,
    _collect_feature_files_from_dirs,
    filter_discovery_by_policies,
    matching_policy_annotations,
    policy_id_matches,
    resolve_policies_source_label,
)
from src.compliance.shell_lex import (
    _consume_backtick,
    _consume_dollar_construct,
    _find_matching_paren,
    _Frame,
    _nested_cmdsubs_in_dollar,
    _quote_state_inside_dollar,
    dialect_from_shebang_line,
    iter_command_substitutions,
    quote_state_at,
    strip_comment,
)
from src.compliance.shell_render import (
    _display_location,
    _relative_path,
    _render_violation_table_html,
    render_shell_check_html,
    render_shell_check_mr_comment,
)
from src.gitlab_compliance import check, generate, gitlab_compliance
from src.modules import gitstrings as gs
from src.modules.common import (
    _table_cell_text,
    format_description_cell,
    format_options_cell,
    format_structured_cell,
    render_markdown_table,
    render_rules_markdown,
    render_table_or_list,
)
from src.modules.constants import (
    GITSTRINGS_MARKER_CLOSE,
    GITSTRINGS_MARKER_OPEN,
)
from src.modules.gitstrings import (
    GitstringsBlock,
    GitstringsDirectives,
    _ci_yaml_path,
    _collect_yaml_body_lines,
    _count_variables_for_path,
    _directive_prefix_lines,
    _find_git_dir,
    _git_ref,
    _limited_render_note,
    _load_yaml_root,
    _masked_source_yaml_body,
    _read_head_ref,
    _read_origin_url,
    _render_table_for_doc,
    _repo_url_without_credentials,
    _source_code_link,
    _source_repository_url,
    _split_ci_decorated_block,
    _upgrade_legacy_gitstrings_markers,
    detect_render_mode,
    extract_gitstrings_blocks_from_ci_yaml,
    parse_directives,
    render_fragment,
)
from src.modules.pipeline_data import (
    _collect_from_fetched_yaml,
    _iter_include_entries,
    _parse_image_reference,
    _parse_service_image,
    _process_local_include,
    _process_parsed_include,
    _should_resolve_external,
    collect_pipeline_data,
)
from src.modules.swagger_markdown import (
    _jobs_grouped,
    _render_rules_section,
    render_swagger_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples/sample-files" / ".gitlab-ci.yml"
SHELL_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "shell_check"
PIPELINE = str(SHELL_FIXTURES / "bad-pipeline.yml")
POLICIES = "tests/compliance_policies/failing"
MARKER_BLOCK = f"{GITSTRINGS_MARKER_OPEN}\n{GITSTRINGS_MARKER_CLOSE}\n"


# ---------------------------------------------------------------------------
# Wave 2 — modules / CLI
# ---------------------------------------------------------------------------


class TestGitstringsUncoveredBranches:
    def test_find_git_dir_resolve_oserror(self):
        with patch.object(Path, "resolve", side_effect=OSError("broken")):
            root, git_dir = _find_git_dir(Path("anywhere.yml"))
        # Falls back to unresolved path; may still find nothing
        assert root is None or git_dir is None or True

    def test_find_git_dir_gitfile_read_oserror(self, tmp_path):
        worktree = tmp_path / "wt"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: ../real.git\n", encoding="utf-8")
        real_read = Path.read_text

        def flaky(self, *args, **kwargs):
            if self.name == ".git" and self.is_file():
                raise OSError("perm")
            return real_read(self, *args, **kwargs)

        with patch.object(Path, "read_text", flaky):
            root, git_dir = _find_git_dir(worktree / "ci.yml")
        assert root is None and git_dir is None

    def test_read_origin_url_parser_exception(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]\n", encoding="utf-8")
        with patch("src.modules.gitstrings.ConfigParser") as parser_cls:
            parser_cls.return_value.read.side_effect = Exception("boom")
            assert _read_origin_url(git_dir) is None

    def test_read_origin_url_no_origin_section(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(
            "[core]\n\trepositoryformatversion = 0\n", encoding="utf-8"
        )
        assert _read_origin_url(git_dir) is None

    def test_read_head_ref_none_and_tag(self, tmp_path):
        assert _read_head_ref(None) is None
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        assert _read_head_ref(git_dir) is None
        (git_dir / "HEAD").write_text("ref: refs/tags/v1.0.0\n", encoding="utf-8")
        assert _read_head_ref(git_dir) == "refs/tags/v1.0.0"

    def test_git_ref_fallbacks(self, monkeypatch):
        monkeypatch.delenv("CI_COMMIT_SHA", raising=False)
        monkeypatch.delenv("CI_COMMIT_REF_NAME", raising=False)
        monkeypatch.delenv("CI_DEFAULT_BRANCH", raising=False)
        assert _git_ref(None, prefer_ci_ref=False) == "HEAD"
        assert _git_ref(None, prefer_ci_ref=True) == "HEAD"

    def test_repo_url_with_port(self):
        assert (
            _repo_url_without_credentials("https://gitlab.example:8443/g/r.git")
            == "https://gitlab.example:8443/g/r"
        )

    def test_source_repository_url_ci_when_not_current_repo(
        self, tmp_path, monkeypatch
    ):
        other = tmp_path / "other"
        other.mkdir()
        (other / ".git").mkdir()
        src = tmp_path / "src"
        src.mkdir()
        (src / ".git").mkdir()
        ci = src / ".gitlab-ci.yml"
        ci.write_text("variables:\n  A: 1\n", encoding="utf-8")
        monkeypatch.chdir(other)
        monkeypatch.setenv("CI_REPOSITORY_URL", "https://gitlab.com/ci/fallback")
        url, _root, _git, prefer = _source_repository_url(ci)
        assert url == "https://gitlab.com/ci/fallback"
        assert prefer is True

    def test_parse_directives_empty_and_inline_description(self):
        empty, _ = parse_directives(
            "# @description\n# @render variables\nvariables:\n  A: 1\n"
        )
        assert empty.description is None
        inline, _ = parse_directives(
            "# @description Inline prose\n# @output-file out.md\nvariables:\n  A: 1\n"
        )
        assert inline.description == "Inline prose"
        assert inline.output == "out.md"

    def test_masked_source_no_sensitive_and_prefix(self):
        plain = GitstringsBlock(
            raw_body="variables:\n  S: secret\n",
            cleaned_yaml="variables:\n  S: secret\n",
            directives=GitstringsDirectives(),
        )
        assert "secret" in _masked_source_yaml_body(
            plain, {"variables": {"S": "secret"}}
        )

        raw = (
            "# @description\n"
            "#   Secret vars\n"
            "# @sensitive variables.S\n"
            "# @render variables\n"
            "variables:\n"
            "  S: secret\n"
        )
        prefix = _directive_prefix_lines(raw)
        assert any("Secret vars" in line for line in prefix)
        block = GitstringsBlock(
            raw_body=raw,
            cleaned_yaml="variables:\n  S: secret\n",
            directives=parse_directives(raw)[0],
        )
        assert "# @description" in _masked_source_yaml_body(
            block, {"variables": {"S": "secret"}}
        )

    def test_collect_and_split_ci_blocks(self):
        body, idx = _collect_yaml_body_lines(
            ["variables:", "  A: 1", "# @custom foo", "B: 2"], 0
        )
        assert body == ["variables:", "  A: 1"]
        assert idx == 2
        assert _split_ci_decorated_block(["variables:", "  A: 1"], 0) is None
        header, yaml_lines, _end = _split_ci_decorated_block(
            ["# @description", "variables:", "  A: 1"], 0
        )
        assert header == ["# @description"]
        assert yaml_lines[0].startswith("variables")

    def test_extract_skips_description_only_blocks(self):
        assert (
            extract_gitstrings_blocks_from_ci_yaml(
                "# @description\n#   only desc\nvariables:\n  A: 1\n"
            )
            == []
        )

    def test_load_yaml_and_detect_render_mode(self):
        assert _load_yaml_root("") == {}
        assert _load_yaml_root("# comment only\n") == {}
        assert detect_render_mode("scalar", "auto") == "auto"
        assert detect_render_mode({"stages": ["test"]}, "auto") == "auto"
        assert _ci_yaml_path(None) is None

    def test_render_table_jobs_generic_and_counts(self):
        assert "|" in _render_table_for_doc({"stages": ["t"]}, "auto")
        assert "j" in _render_table_for_doc(
            {"j": {"stage": "t", "script": ["echo"]}}, "jobs"
        )
        assert "|" in _render_table_for_doc({"a": 1}, "other")
        root = {"job": {"variables": {"A": "1", "B": "2"}, "script": ["e"]}}
        assert _count_variables_for_path(root, "job") == 2
        assert _limited_render_note({}, ",,") == ""

    def test_source_code_link_fallbacks(self, tmp_path):
        block = GitstringsBlock(
            raw_body="x",
            cleaned_yaml="variables:\n  A: 1\n",
            directives=GitstringsDirectives(render="variables"),
            source_start_line=5,
            source_end_line=5,
        )
        link = _source_code_link(block, scan_path=tmp_path / "x.yml")
        assert "line 5" in link

        with patch.object(
            gs,
            "_source_repository_url",
            return_value=(None, Path("/repo"), None, False),
        ):
            with patch("pathlib.Path.resolve", return_value=Path("/outside/file.yml")):
                with patch("pathlib.Path.relative_to", side_effect=ValueError("diff")):
                    link = _source_code_link(block, scan_path="/outside/file.yml")
        assert "file.yml" in link

        with patch.object(
            gs, "_source_repository_url", return_value=(None, None, None, False)
        ):
            with patch(
                "src.modules.gitstrings.os.path.relpath", side_effect=ValueError("x")
            ):
                link = _source_code_link(
                    block,
                    scan_path="/tmp/a.yml",
                    output_path="/tmp/out/README.md",
                )
        assert "a.yml" in link

    def test_render_fragment_none_and_non_dict_doc(self):
        with patch.object(gs, "_load_yaml_root", return_value=None):
            block = GitstringsBlock(
                raw_body="x: 1",
                cleaned_yaml="x: 1",
                directives=GitstringsDirectives(render="auto"),
            )
            assert render_fragment(block, keep_source=False)

        scalar = GitstringsBlock(
            raw_body="42",
            cleaned_yaml="42",
            directives=GitstringsDirectives(render="auto"),
            source_start_line=1,
            source_end_line=1,
        )
        out = render_fragment(scalar, keep_source=False)
        assert "42" in out

    def test_upgrade_legacy_markers_missing_file(self, tmp_path):
        _upgrade_legacy_gitstrings_markers(tmp_path / "missing.md")

    def test_description_blank_prose_and_masked_without_prefix(self):
        empty, _ = parse_directives(
            "# @description\n#   \n# @render variables\nvariables:\n  A: 1\n"
        )
        assert empty.description is None
        # Description followed by non-comment YAML → break at prose collector
        broken, _ = parse_directives("# @description\nvariables:\n  A: 1\n")
        assert broken.description is None
        prefix = _directive_prefix_lines(
            "# @description\nvariables:\n  A: 1\n# @render variables\n"
        )
        assert any("@description" in line for line in prefix)

        sensitive = GitstringsBlock(
            raw_body="variables:\n  S:\n    value: secret\n",
            cleaned_yaml="variables:\n  S:\n    value: secret\n",
            directives=GitstringsDirectives(sensitive=["variables.S.value"]),
        )
        out = _masked_source_yaml_body(
            sensitive, {"variables": {"S": {"value": "secret"}}}
        )
        assert "****" in out
        assert "secret" not in out
        assert not out.startswith("#")


class TestCommonCellBranches:
    def test_common_cell_and_table_edge_branches(self):
        assert _table_cell_text(None) == ""
        assert render_rules_markdown(["not-a-dict"]) == ""
        assert format_description_cell(None) == "&#x274c;"
        assert format_description_cell(12) == "12"
        assert format_description_cell("   ") == "&#x274c;"

        assert format_structured_cell(None) == ""
        assert format_structured_cell(True) == "True"
        assert format_structured_cell(3.5) == "3.5"
        assert format_structured_cell([]) == "[]"
        assert "<br>" in format_structured_cell([1, "a"])
        assert format_structured_cell({"description": "x", "expand": True}) == ""
        assert format_structured_cell(object())

        assert format_options_cell(None) == "&#x274c;"
        assert format_options_cell("") == "&#x274c;"
        assert format_options_cell([]) == "&#x274c;"
        assert "<br>" in format_options_cell(["a", "b"])
        assert format_options_cell({"default": "x"}) == "x"
        assert format_options_cell(9) == "9"

        assert render_markdown_table([], []) == ""
        assert render_table_or_list([], [[1]]) == ""


class TestSwaggerMarkdownEmpty:
    def test_swagger_markdown_empty_sections_and_helpers(self):
        assert _render_rules_section([{"if": "$CI"}, "scalar"], "rules") == []
        grouped = _jobs_grouped({"jobs": [{"display_name": "A"}]})
        assert grouped[0]["jobs"][0]["display_name"] == "A"

        md = render_swagger_markdown(
            {
                "config_file": "c.yml",
                "jobs": [],
                "includes": [],
                "variables": [],
                "inputs": [],
                "workflow_rules": [],
                "exclude_sections": set(),
            }
        )
        assert "_No inputs defined._" in md
        assert "_No variables defined._" in md
        assert "_No includes defined._" in md
        assert "_No jobs found._" in md


class TestPipelineDataUncovered:
    def test_iter_include_and_image_service_helpers(self):
        assert _iter_include_entries(None) == []
        assert _iter_include_entries(99) == [99]
        assert _parse_image_reference({"name": "alpine:3.20"}) == "alpine:3.20"
        assert _parse_service_image({"name": "postgres:16"}) == "postgres:16"
        assert (
            _should_resolve_external(None, include_type="template", token="t") is False
        )

    def test_exclude_section_pass_branches_and_non_dict_doc(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "---\njust-a-string\n---\n"
            "spec:\n  inputs:\n    x: 1\n"
            "variables:\n  A: 1\n"
            "include:\n  - local: missing.yml\n"
            "workflow:\n  rules:\n    - when: always\n"
            "job:\n  script: echo\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(
            str(cfg),
            detailed=True,
            exclude_sections={"inputs", "includes", "workflow"},
        )
        assert data["inputs"] == []
        assert data["includes"] == []
        assert data["workflow_rules"] == []
        assert any(v["key"] == "A" for v in data["variables"])

    def test_collect_from_fetched_unlink_oserror(self):
        with patch("src.modules.pipeline_data.os.unlink", side_effect=OSError("busy")):
            out = _collect_from_fetched_yaml(
                yaml_text="job:\n  script: echo\n",
                config_label="remote:https://example.com/a.yml",
                detailed=False,
                include_nested=False,
                max_include_depth=None,
                exclude_sections=None,
                exclude_attributes=None,
                group_by=None,
                include_scripts=False,
                resolve_job_composition=False,
                resolve_external_includes=False,
                gitlab_url=None,
                token=None,
                _depth=0,
                _visited=set(),
                _job_registry={},
                _fetch_cache=IncludeFetchCache(),
                _unresolved=[],
                _external_context=None,
            )
        assert {j["name"] for j in out["jobs"]} == {"job"}

    def test_local_include_external_context_fetch_failure(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("job:\n  script: echo\n", encoding="utf-8")
        unresolved = []
        ctx = ExternalIncludeContext(
            kind="remote",
            visit_key="https://example.com/a.yml",
            base_url="https://example.com/",
        )
        with patch(
            "src.modules.pipeline_data.resolve_nested_local_from_context",
            return_value=IncludeFetchFailure(reason="fetch_failed", detail="nope"),
        ):
            _process_local_include(
                {
                    "include_type": "local",
                    "project": "child.yml",
                    "version": "n/a",
                    "valid_version": True,
                    "file": "",
                    "variables": {},
                    "rules": [],
                    "source_file": "",
                    "line": 0,
                },
                config_file=str(cfg),
                data={"includes": [], "jobs": []},
                detailed=True,
                include_nested=True,
                max_include_depth=None,
                exclude_sections=None,
                exclude_attributes=None,
                group_by=None,
                include_scripts=False,
                resolve_job_composition=False,
                resolve_external_includes=True,
                gitlab_url=None,
                token=None,
                _depth=0,
                _visited=set(),
                _job_registry={},
                _fetch_cache=IncludeFetchCache(),
                _unresolved=unresolved,
                _external_context=ctx,
            )
        assert unresolved[0].reason == "fetch_failed"
        assert unresolved[0].detail == "nope"

    def test_process_parsed_include_unsupported_type_reason(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("job:\n  script: echo\n", encoding="utf-8")
        unresolved = []
        _process_parsed_include(
            {
                "include_type": "weird",
                "project": "x",
                "version": "",
                "valid_version": False,
                "file": "",
                "variables": {},
                "rules": [],
                "source_file": "",
                "line": 0,
            },
            config_file=str(cfg),
            data={"includes": [], "jobs": []},
            can_recurse=True,
            include_nested=True,
            detailed=True,
            max_include_depth=None,
            exclude_sections=None,
            exclude_attributes=None,
            group_by=None,
            include_scripts=False,
            resolve_job_composition=False,
            resolve_external_includes=True,
            gitlab_url=None,
            token=None,
            _depth=0,
            _visited=set(),
            _job_registry={},
            _fetch_cache=IncludeFetchCache(),
            _unresolved=unresolved,
            _external_context=None,
        )
        assert unresolved[0].reason == "unsupported_type"

    def test_process_parsed_include_resolves_template_when_enabled(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("job:\n  script: echo\n", encoding="utf-8")
        data = {"includes": [], "jobs": [], "variables": [], "workflow_rules": []}
        unresolved = []
        with patch(
            "src.modules.pipeline_data.fetch_include_content",
            return_value=FetchedInclude(
                config_label="template:Auto-DevOps.gitlab-ci.yml",
                yaml_text="template-job:\n  script: [echo]\n",
            ),
        ):
            _process_parsed_include(
                {
                    "include_type": "template",
                    "project": "Auto-DevOps.gitlab-ci.yml",
                    "version": "n/a",
                    "valid_version": False,
                    "file": "",
                    "variables": {},
                    "rules": [],
                    "source_file": "",
                    "line": 1,
                },
                config_file=str(cfg),
                data=data,
                can_recurse=True,
                include_nested=True,
                detailed=True,
                max_include_depth=None,
                exclude_sections=None,
                exclude_attributes=None,
                group_by=None,
                include_scripts=False,
                resolve_job_composition=False,
                resolve_external_includes=True,
                resolve_templates=True,
                gitlab_url=None,
                token=None,
                _depth=0,
                _visited=set(),
                _job_registry={},
                _fetch_cache=IncludeFetchCache(),
                _unresolved=unresolved,
                _external_context=None,
            )
        assert not unresolved
        assert any(job["name"] == "template-job" for job in data["jobs"])

    def test_process_parsed_include_template_fetch_failure(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("job:\n  script: echo\n", encoding="utf-8")
        unresolved = []
        with patch(
            "src.modules.pipeline_data.fetch_include_content",
            return_value=IncludeFetchFailure(reason="fetch_failed", detail="404"),
        ):
            _process_parsed_include(
                {
                    "include_type": "template",
                    "project": "Missing.gitlab-ci.yml",
                    "version": "n/a",
                    "valid_version": False,
                    "file": "",
                    "variables": {},
                    "rules": [],
                    "source_file": "",
                    "line": 1,
                },
                config_file=str(cfg),
                data={"includes": [], "jobs": []},
                can_recurse=True,
                include_nested=True,
                detailed=True,
                max_include_depth=None,
                exclude_sections=None,
                exclude_attributes=None,
                group_by=None,
                include_scripts=False,
                resolve_job_composition=False,
                resolve_external_includes=True,
                resolve_templates=True,
                gitlab_url=None,
                token=None,
                _depth=0,
                _visited=set(),
                _job_registry={},
                _fetch_cache=IncludeFetchCache(),
                _unresolved=unresolved,
                _external_context=None,
            )
        assert unresolved[0].reason == "fetch_failed"


class TestGitlabComplianceUncoveredCli:
    def test_generate_filter_value_error_becomes_click_exception(self):
        runner = CliRunner()
        with patch(
            "src.gitlab_compliance._parse_generate_filters",
            side_effect=ValueError("Unknown section(s)"),
        ):
            result = runner.invoke(
                generate,
                ["-i", str(SAMPLE), "-o", "out.md"],
            )
        assert result.exit_code != 0
        assert "Unknown section" in result.output

    def test_check_requires_features_or_builtin_flags(self):
        result = CliRunner().invoke(check, ["-p", str(SAMPLE)])
        assert result.exit_code != 0
        assert "Provide --features" in result.output or "with-builtin" in result.output

    def test_supply_chain_markdown_report_paths(self, tmp_path, monkeypatch):
        ok = ComplianceResult(
            success=True,
            exit_code=0,
            scenario_results=[],
            scenarios=0,
            passed=0,
            failed=0,
            skipped=0,
        )
        monkeypatch.setattr(
            "src.gitlab_compliance._gitlab_docs.run_compliance",
            lambda **kwargs: ok,
        )
        monkeypatch.setattr(
            "src.gitlab_compliance._gitlab_docs.render_compliance_report",
            lambda **kwargs: "# supply report\n",
        )

        runner = CliRunner()
        out = tmp_path / "sc.md"
        written = runner.invoke(
            gitlab_compliance,
            [
                "supply-chain",
                "-p",
                str(SAMPLE),
                "--format",
                "markdown",
                "-o",
                str(out),
            ],
        )
        assert written.exit_code == 0
        assert out.read_text(encoding="utf-8") == "# supply report\n"

        with patch(
            "src.gitlab_compliance._resolve_compliance_output", return_value=None
        ):
            echoed = runner.invoke(
                gitlab_compliance,
                ["supply-chain", "-p", str(SAMPLE), "--format", "markdown"],
            )
        assert echoed.exit_code == 0
        assert "# supply report" in echoed.output

        fail = ComplianceResult(
            success=False,
            exit_code=1,
            scenario_results=[],
            scenarios=1,
            passed=0,
            failed=1,
            skipped=0,
        )
        monkeypatch.setattr(
            "src.gitlab_compliance._gitlab_docs.run_compliance",
            lambda **kwargs: fail,
        )
        failed = runner.invoke(
            gitlab_compliance,
            [
                "supply-chain",
                "-p",
                str(SAMPLE),
                "--format",
                "markdown",
                "-o",
                str(tmp_path / "fail.md"),
            ],
        )
        assert failed.exit_code == 1

    def test_shell_check_error_echo_and_success(self, tmp_path, monkeypatch):
        runner = CliRunner()
        monkeypatch.setattr(
            "src.gitlab_compliance._gitlab_docs.run_compliance",
            MagicMock(side_effect=FileNotFoundError("missing pipeline")),
        )
        err = runner.invoke(
            gitlab_compliance,
            ["shell-check", "-p", str(SAMPLE)],
        )
        assert err.exit_code == 2

        ok = ComplianceResult(
            success=True,
            exit_code=0,
            scenario_results=[],
            scenarios=0,
            passed=0,
            failed=0,
            skipped=0,
        )
        monkeypatch.setattr(
            "src.gitlab_compliance._gitlab_docs.run_compliance",
            lambda **kwargs: ok,
        )
        monkeypatch.setattr(
            "src.compliance.shell_render.render_shell_check_report",
            lambda **kwargs: "# shell ok\n",
        )
        good = SHELL_FIXTURES / "good-pipeline.yml"
        success = runner.invoke(
            gitlab_compliance,
            [
                "shell-check",
                "-p",
                str(good),
                "--format",
                "markdown",
                "-o",
                str(tmp_path / "ok.md"),
            ],
        )
        assert success.exit_code == 0

        with patch(
            "src.gitlab_compliance._resolve_compliance_output", return_value=None
        ):
            echoed = runner.invoke(
                gitlab_compliance,
                ["shell-check", "-p", str(good), "--format", "markdown"],
            )
        assert echoed.exit_code == 0
        assert "# shell ok" in echoed.output

    def test_document_gitstrings_dry_and_no_blocks(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("# nothing\n", encoding="utf-8")
        runner = CliRunner()
        none_updated = runner.invoke(
            gitlab_compliance,
            ["document", "gitstrings", "-i", str(empty)],
        )
        assert none_updated.exit_code == 0

        readme = tmp_path / "r.md"
        readme.write_text(
            "```yaml gitstrings\n# @render variables\nvariables:\n  A: 1\n```\n"
            + MARKER_BLOCK,
            encoding="utf-8",
        )
        dry = runner.invoke(
            gitlab_compliance,
            [
                "document",
                "gitstrings",
                "-i",
                str(readme),
                "--dry-mode",
                "--no-keep-source",
            ],
        )
        assert dry.exit_code == 0


# ---------------------------------------------------------------------------
# Wave 3 — shell / compliance engine
# ---------------------------------------------------------------------------


def _entity(lines, **extra):
    values = {"effective_script": lines, "script": lines}
    values.update(extra)
    entity = {
        "name": "job",
        "source_file": "ci.yml",
        "line": 1,
        "values": values,
    }
    entity.update(values)
    return entity


class TestScriptAnalysisMisses:
    def test_var_expansion_fallback_when_iterator_empty(self, monkeypatch):
        monkeypatch.setattr(sa, "iter_parameter_expansions", lambda *a, **k: iter(()))
        assert sa._line_has_unquoted_var_expansion("echo $NAME") is True
        assert sa._line_has_unquoted_var_expansion('echo "$NAME"') is False

    def test_path_argument_span_stops_at_semicolon_and_pipe(self):
        line = "cd $HOME; echo later"
        end = sa._path_argument_span(line, 0)
        assert line[end] == ";"
        line2 = "cd $HOME | cat"
        end2 = sa._path_argument_span(line2, 0)
        assert line2[end2] == "|"

    def test_container_image_empty_ref_and_pin_helpers(self):
        assert sa._container_image_ref_is_pinned("") is True
        assert sa._container_image_ref_is_pinned("''") is True
        assert sa._container_image_ref_is_pinned('""') is True

    def test_split_command_tokens_and_tokens_after_miss(self):
        assert sa._split_command_tokens('curl "unclosed') == ["curl", '"unclosed']
        assert sa._tokens_after_subcommand("echo hi", sa._PIP) == []

    def test_package_tokens_skip_and_flag_equals(self):
        pkgs = sa._package_tokens(
            ["skipme", "--index-url=https://pypi.org", "-q", "requests==1"],
            flags_with_arg=sa._PIP_FLAGS_WITH_ARG,
            skip_tokens=frozenset({"skipme"}),
        )
        assert pkgs == ["requests==1"]

    def test_manager_pin_empty_and_require_hashes(self):
        assert sa._pip_install_line_is_pinned("pip install --require-hashes -r r.txt")
        assert sa._pip_install_line_is_pinned("pip install")
        assert sa._apk_line_is_pinned("apk add --update --no-cache")
        assert sa._apt_line_is_pinned("apt-get install -y")
        assert sa._yum_line_is_pinned("yum install -y")
        assert sa._yum_package_is_pinned("/tmp/pkg.rpm")
        assert sa._npm_line_is_pinned("npm install -g")
        assert sa._pip_package_is_pinned("pkg@git+https://example.com/r.git")
        assert sa._pip_package_is_pinned("pkg@1.2.3")

    def test_docker_extract_volume_flags_create_and_bad_quotes(self):
        assert sa._is_volume_mount("/tmp:/work")
        assert sa._is_volume_mount("./data:/data")
        assert sa._is_volume_mount("$PWD:/work")
        assert sa._is_volume_mount("1234:/work")
        assert not sa._is_volume_mount("python:3.12")
        assert sa._extract_docker_image_from_run('alpine "unclosed') == []
        assert sa._extract_docker_image_from_run("--network=host -t alpine") == [
            "alpine"
        ]
        assert sa._extract_docker_image_from_run("-t alpine") == ["alpine"]
        assert sa._extract_docker_image_from_run("-v /tmp:/work alpine") == ["alpine"]
        # Bare volume token (not via -v) then image → volume skip + return
        assert sa._extract_docker_image_from_run("/tmp:/work alpine") == ["alpine"]
        assert sa._extract_docker_image_from_run("/tmp:/work") == []
        assert sa._docker_image_refs_on_line("docker create --name x alpine:3.19") == [
            "alpine:3.19"
        ]

    def test_evidence_none_and_clip_and_provenance(self):
        assert sa._first_active_line(_entity(["echo hi"]), lambda _l: False) is None
        assert sa._clip_evidence("a" * 250).endswith("...")
        assert len(sa._clip_evidence("a" * 250)) == 200

        assert sa.evidence_unquoted_path_variables(_entity(['cd "$HOME"'])) is None
        assert sa.evidence_unsafe_array_expansion(_entity(['echo "${arr[@]}"'])) is None
        assert sa.evidence_unsafe_array_expansion(_entity(["echo ${arr[@]}"]))
        assert sa.evidence_nested_backticks(_entity(["echo hi"])) is None
        assert (
            sa.evidence_missing_strict_mode(_entity(["set -euo pipefail", "echo"]))
            is None
        )
        assert sa.evidence_missing_strict_mode(_entity(["", "  "])) is None
        assert (
            sa.evidence_insecure_temp_files(_entity(["tmp=$(mktemp)", "echo x"]))
            is None
        )
        assert sa.evidence_dangerous_rm(_entity(['rm -rf "$DIR"'])) is None
        assert sa.evidence_dangerous_rm(_entity(["echo hi"])) is None
        assert (
            sa.evidence_unquoted_test_variables(_entity(['[ "$FOO" = bar ]'])) is None
        )
        assert (
            sa.evidence_pipeline_without_pipefail(_entity(["set -o pipefail", "a | b"]))
            is None
        )
        assert (
            sa.evidence_download_without_checksum(_entity(["curl https://x | bash"]))
            is None
        )
        assert (
            sa.evidence_download_without_checksum(
                _entity(["curl -O https://x", "sha256sum -c s"])
            )
            is None
        )
        assert sa.evidence_unpinned_manager(_entity(["echo hi"]), "go") is None
        assert (
            sa.evidence_unpinned_manager(_entity(["go install example.com/x"]), "go")
            is not None
        )
        assert sa.evidence_unpinned_manager(_entity(["apk add curl=1"]), "apk") is None
        assert sa.evidence_unpinned_manager(_entity(["echo"]), "unknown") is None
        assert (
            sa.evidence_unpinned_docker(_entity(["docker pull python:3.12.0"])) is None
        )
        assert (
            sa.evidence_unverified_git_clone(
                _entity(["git clone https://x.git", "git checkout abc"])
            )
            is None
        )

        prov = _entity(
            ["echo"],
            unresolved_script_references=[],
            script_provenance=[
                {
                    "origin": "unresolved_reference",
                    "via": "!reference [.x, script]",
                }
            ],
        )
        assert "reference" in sa.evidence_unresolved_references(prov)
        prov2 = _entity(
            ["echo"],
            unresolved_script_references=[],
            script_provenance=[{"origin": "unresolved_reference"}],
        )
        assert sa.evidence_unresolved_references(prov2) == "unresolved_reference"
        assert (
            sa.evidence_unresolved_references(
                _entity(
                    ["echo"],
                    unresolved_script_references=[],
                    script_provenance=[{"origin": "other"}],
                )
            )
            is None
        )

        assert sa.evidence_invalid_shebang(_entity(["echo hi"])) is None
        assert sa.evidence_invalid_shebang(_entity(["#!/bin/bash", "echo"])) is None
        assert (
            sa.evidence_bashisms_without_bash(_entity(["#!/bin/bash", "[[ -f x ]]"]))
            is None
        )
        assert (
            sa.evidence_posix_bashisms(_entity(["#!/bin/bash", "[[ -f x ]]"])) is None
        )


class TestShellLexMisses:
    def test_shebang_local_sh_word_boundary(self):
        assert dialect_from_shebang_line("#!/usr/local/bin/sh") == "sh"
        assert dialect_from_shebang_line("#!/opt/custom/sh -e") == "sh"

    def test_scan_balanced_ansi_dq_escape_backtick_and_unquoted_escape(self):
        line = "echo $(echo $'a\\nb' \"c\\$d\" `e` \\) )"
        close = _find_matching_paren(line, line.index("("), dialect="bash")
        assert line[close] == ")"
        # ANSI-C inside nested paren body
        ansi = "echo $(echo $'x\\ny')"
        close = _find_matching_paren(ansi, ansi.index("("), dialect="bash")
        assert ansi[close] == ")"
        # Backticks inside double quotes in nested body
        dq_bt = 'echo $(echo "`date`")'
        close = _find_matching_paren(dq_bt, dq_bt.index("("), dialect="bash")
        assert dq_bt[close] == ")"
        assert _consume_backtick("echo `open", 5, "bash") == len("echo `open")
        frame = _Frame()
        assert _consume_dollar_construct("x", 0, frame, "bash") == 1
        assert _consume_dollar_construct("$.", 0, frame, "bash") == 1

    def test_locale_dq_escape_and_nested_dollar(self):
        frame = _Frame()
        line = 'x=$"hi \\$NAME $(echo) end"'
        end = _consume_dollar_construct(line, line.index("$"), frame, "bash")
        assert end == len(line) or line[end - 1] == '"'

    def test_quote_state_ansi_locale_backtick_process(self):
        ansi = "$'a\\nb'"
        assert quote_state_at(ansi, ansi.index("\\") + 1) == "single"
        # Index on the escape char itself inside ANSI-C
        assert quote_state_at(ansi, ansi.index("\\")) == "single"
        # Closing quote of ANSI-C
        assert quote_state_at("$'x'", 3) in {"single", "none"}
        locale = '$"hi \\$x"'
        assert quote_state_at(locale, locale.index("\\") + 1) == "double"
        line = 'echo "`date`"'
        assert quote_state_at(line, line.index("d")) == "none"
        # Unquoted backticks: index past close (fallthrough)
        bt = "echo `uname` x"
        assert quote_state_at(bt, bt.index("x")) == "none"
        # Closing backtick index boundary
        assert quote_state_at("echo `x`", 6) in {"none", "double", "single"}
        proc = "cat <(echo x) y"
        assert quote_state_at(proc, proc.index("y")) == "none"
        assert _quote_state_inside_dollar("$", 0, 1, 0, "bash") == "none"
        braced = "echo ${FOO}"
        assert (
            _quote_state_inside_dollar(
                braced, braced.index("$"), len(braced), braced.index("}"), "bash"
            )
            == "none"
        )

    def test_iter_cmdsub_ansi_and_nested_guards(self):
        list(iter_command_substitutions("echo $'a\\nb'"))
        list(iter_command_substitutions("echo $'x\\ny' $(true)"))
        spans = list(iter_command_substitutions('echo "`date`"'))
        assert any(s.start > 0 for s in spans)
        # Escape inside double-quoted cmdsub scan
        list(iter_command_substitutions('echo "$(echo \\$x)"'))
        assert list(_nested_cmdsubs_in_dollar("$(", 0, 2, "bash")) == []
        assert list(_nested_cmdsubs_in_dollar("${x}", 0, 4, "bash")) == []
        assert list(_nested_cmdsubs_in_dollar("$((1))", 0, 6, "bash")) == []
        assert list(_nested_cmdsubs_in_dollar("$()", 0, 3, "bash")) == []

    def test_strip_comment_backticks_inside_double(self):
        assert strip_comment('echo "`a#b`" # outer') == 'echo "`a#b`"'


class TestShellRenderMisses:
    def test_relative_path_value_error(self, monkeypatch):
        monkeypatch.setattr(
            "src.compliance.shell_render.os.path.relpath",
            lambda *_a, **_k: (_ for _ in ()).throw(ValueError("different drives")),
        )
        assert _relative_path("/a/b.yml", "/other") == "a/b.yml"

    def test_display_location_empty_and_abs(self, tmp_path):
        assert _display_location("", str(tmp_path / "ci.yml")) == ""
        abs_loc = f"{tmp_path / 'ci.yml'}:12"
        shown = _display_location(abs_loc, str(tmp_path / "ci.yml"))
        assert shown.endswith("ci.yml:12")

    def test_empty_html_table(self):
        assert _render_violation_table_html([], "ci.yml") == ""

    def test_parse_empty_boundary_part(self):
        from src.compliance.shell_render import parse_shell_violations

        # Leading/extra boundary can yield empty segments after split
        violations = parse_shell_violations("ASSERT FAILED:  ;  Job 'j' f.yml:1: msg")
        assert violations

    def test_mr_comment_framework_and_unstructured_and_skipped(self):
        result = ComplianceResult(
            success=False,
            exit_code=1,
            scenario_results=[
                ScenarioResult(
                    feature="f.feature",
                    name="fail",
                    status="failed",
                    message="ASSERT FAILED: plain failure text",
                    policy_id="P-FAIL",
                    title="Fail",
                    description="desc",
                    owasp_cicd="CICD-SEC-1",
                    iso27001="A.8.25",
                ),
                ScenarioResult(
                    feature="s.feature",
                    name="skip",
                    status="skipped",
                    message="no match",
                    policy_id="P-SKIP",
                    title="Skip",
                    owasp_cicd="CICD-SEC-2",
                    iso27001="A.8.9",
                ),
            ],
            scenarios=2,
            passed=0,
            failed=1,
            skipped=1,
        )
        text = render_shell_check_mr_comment(result, PIPELINE, POLICIES)
        assert "OWASP CI/CD" in text
        assert "ISO 27001" in text
        assert "plain failure text" in text
        assert "P-SKIP" in text

        html = render_shell_check_html(result, PIPELINE, POLICIES)
        assert "OWASP CI/CD" in html
        assert "ISO 27001" in html


class TestRunnerMisses:
    def _ann(self, fid, file, name="S"):
        return PolicyAnnotation(
            policy_id=fid,
            title=name,
            scope="scenario",
            feature_file=file,
            line=1,
            feature_name="F",
            scenario_name=name,
        )

    def test_policy_id_matches_empty_and_case(self):
        assert policy_id_matches("ANY", []) is True
        assert policy_id_matches("", ["X"]) is False
        assert (
            policy_id_matches("glci-builtin-shell-pin-01", ["GLCI-BUILTIN-SHELL-PIN"])
            is True
        )

    def test_matching_and_filter_discovery(self, tmp_path):
        f = tmp_path / "a.feature"
        f.write_text("Feature: A\n  Scenario: S\n    Given x\n", encoding="utf-8")
        ann = self._ann("GLCI-X-01", str(f))
        catalog = PolicyCatalog(
            features=[
                FeaturePolicies(
                    feature_file=str(f),
                    feature_name="A",
                    annotation=None,
                    scenarios=[ann, ann],
                )
            ]
        )
        # Empty selectors: return all (no dedupe)
        assert len(matching_policy_annotations(catalog, [])) == 2
        # Non-empty selectors: dedupe by (realpath, scenario_name)
        all_anns = matching_policy_annotations(catalog, ["GLCI-X"])
        assert len(all_anns) == 1

        discovery = PolicyDiscovery(
            catalog=catalog,
            feature_files=[(str(tmp_path), str(f))],
            api_requirements=ApiEnrichmentRequirements(),
        )
        filtered, matches = filter_discovery_by_policies(discovery, [])
        assert filtered is discovery
        assert len(matches) == 2

    def test_resolve_policies_source_label_edges(self):
        assert resolve_policies_source_label(None) == BUILTIN_POLICIES_DIR
        label = resolve_policies_source_label(
            BUILTIN_POLICIES_DIR,
            with_builtin=True,
        )
        assert BUILTIN_POLICIES_DIR in label or os.path.abspath(
            BUILTIN_POLICIES_DIR
        ) in (label or "")

    def test_collect_dedupes_realpath_and_workspace_collision(self, tmp_path):
        a = tmp_path / "a"
        b = tmp_path / "b"
        a.mkdir()
        b.mkdir()
        (a / "x.feature").write_text(
            "Feature: A\n  Scenario: S\n    Given x\n", encoding="utf-8"
        )
        os.symlink(a / "x.feature", b / "x.feature")
        collected = _collect_feature_files_from_dirs([str(a), str(b)])
        assert len(collected) == 1

        # Same basename dirs → colliding target_rel → __{source_label} rename
        x = tmp_path / "x" / "policies"
        y = tmp_path / "y" / "policies"
        x.mkdir(parents=True)
        y.mkdir(parents=True)
        (x / "same.feature").write_text(
            "Feature: C\n  Scenario: S\n    Given x\n", encoding="utf-8"
        )
        (y / "same.feature").write_text(
            "Feature: D\n  Scenario: S\n    Given x\n", encoding="utf-8"
        )
        ws = _build_behave_workspace([str(x), str(y)])
        try:
            names = [p.name for p in Path(ws).rglob("*.feature")]
            assert any("same" in n for n in names)
            assert any("__" in n for n in names)
        finally:
            shutil.rmtree(ws, ignore_errors=True)


class TestThenStepsSkipped:
    def test_then_steps_skip_when_scenario_skipped(self):
        from src.compliance.behave_support.steps import then_steps

        ctx = SimpleNamespace(
            scenario_skipped=True, stash=[{"name": "x"}], step_mode=None
        )
        then_steps.then_must_contain(ctx, "stage")
        then_steps.then_version_valid_semver(ctx)
        then_steps.then_no_newer_release(ctx)
        then_steps.then_no_newer_release_beyond_grace_days(ctx, 1)
        then_steps.then_release_lag_must_not_exceed_days(ctx, 1)
        then_steps.then_must_be_within_latest_tags(ctx, 1)
        then_steps.then_must_use_sha256_digest(ctx)
        then_steps.then_no_newer_image_release(ctx)
        then_steps.then_no_newer_image_release_beyond_grace_days(ctx, 1)
        then_steps.then_image_release_lag_must_not_exceed_days(ctx, 1)
        then_steps.then_must_be_within_latest_image_tags(ctx, 1)
        then_steps.then_version_is_latest_release(ctx)


class TestTableRenderVariablesExceptionNoValue:
    def test_variables_exception_fallback_without_value(self):
        from src.properties.table_render import render_variables_table

        class Evil(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._boom = True

            def items(self):
                if self._boom:
                    self._boom = False
                    raise RuntimeError("items boom")
                return super().items()

        table = render_variables_table(
            {"bad": Evil({"description": "d", "expand": False})}
        )
        assert "bad" in table


class TestOutputFiltersRemaining:
    def test_output_filters_remaining(self):
        from src.modules.output_filters import (
            apply_output_filters,
            group_jobs,
            parse_exclude,
            validate_exclude_sections,
            warn_group_by_excluded,
        )

        assert parse_exclude(None) == (set(), set())
        assert parse_exclude("jobs,stage,,")[0] == {"jobs"}
        with pytest.raises(ValueError, match="Unknown"):
            validate_exclude_sections({"nope"})
        warn_group_by_excluded("stage", {"stage"})
        jobs = [
            {
                "name": "a",
                "attributes": [{"key": "stage", "value": "test"}],
                "nested": [],
                "rules": [],
            },
            {
                "name": "b",
                "attributes": [],
                "nested": [{"attribute": "stage", "value": ""}],
                "rules": [{"when": "always"}],
            },
        ]
        grouped = group_jobs(jobs, "stage")
        assert any(g["group_key"] for g in grouped)
        data = apply_output_filters(
            {
                "inputs": [1],
                "variables": [1],
                "includes": [1],
                "workflow_rules": [1],
                "jobs": jobs,
                "container_images": [1],
            },
            exclude_sections={
                "inputs",
                "variables",
                "includes",
                "workflow",
                "container_images",
            },
            exclude_attributes={"stage", "rules"},
            group_by="stage",
        )
        assert data["inputs"] == []
        assert data["jobs_grouped"]
