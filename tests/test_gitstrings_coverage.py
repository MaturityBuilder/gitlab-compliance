"""Coverage for gitstrings helpers and table_render paths."""

from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import yaml

from src.modules import gitstrings as gs
from src.modules.constants import (
    GITSTRINGS_MARKER_CLOSE,
    GITSTRINGS_MARKER_CLOSE_LEGACY,
    GITSTRINGS_MARKER_OPEN,
    GITSTRINGS_MARKER_OPEN_LEGACY,
)
from src.modules.gitstrings import (
    GitstringsDirectives,
    _blob_url,
    _count_variables_for_path,
    _find_git_dir,
    _git_ref,
    _limited_render_note,
    _load_yaml_root,
    _looks_like_jobs_map,
    _read_head_ref,
    _read_origin_url,
    _render_path_specs,
    _repo_url_without_credentials,
    _source_code_link,
    _source_repository_url,
    _upgrade_legacy_gitstrings_markers,
    detect_render_mode,
    extract_gitstrings_blocks_from_file,
    process_gitstrings,
    render_fragment,
    render_gitstrings_by_output,
    resolve_fragment_output,
    write_gitstrings_block,
)
from src.properties import table_render as tr
from src.properties.yaml_paths import normalize_legacy_render

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples/sample-files" / ".gitlab-ci.yml"

MARKER_BLOCK = f"""{GITSTRINGS_MARKER_OPEN}
{GITSTRINGS_MARKER_CLOSE}
"""


class TestGitstringsGitUrlHelpers:
    def test_find_git_dir_in_repo(self):
        root, git_dir = _find_git_dir(REPO_ROOT)
        assert root is not None
        assert git_dir is not None

    def test_render_jobs_skips_non_dict_job(self):
        assert tr.render_jobs_table({"x": "not-a-dict"}) == ""

    def test_find_git_dir_gitfile_worktree(self, tmp_path):
        worktree = tmp_path / "wt"
        worktree.mkdir()
        real_git = tmp_path / "real.git"
        real_git.mkdir()
        (worktree / ".git").write_text(f"gitdir: {real_git}\n", encoding="utf-8")
        root, git_dir = _find_git_dir(worktree / "ci.yml")
        assert root == worktree
        assert git_dir == real_git.resolve()

    def test_find_git_dir_missing(self, tmp_path):
        root, git_dir = _find_git_dir(tmp_path / "nowhere.yml")
        assert root is None
        assert git_dir is None

    def test_read_origin_url_missing_config(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        assert _read_origin_url(git_dir) is None

    def test_source_code_link_with_repository(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        config = git_dir / "config"
        parser = ConfigParser()
        parser.add_section('remote "origin"')
        parser.set('remote "origin"', "url", "https://gitlab.com/g/r.git")
        with config.open("w", encoding="utf-8") as handle:
            parser.write(handle)
        ci = tmp_path / ".gitlab-ci.yml"
        ci.write_text("# @render variables\nvariables:\n  A: 1\n", encoding="utf-8")
        text = ci.read_text(encoding="utf-8")
        blocks = gs.extract_gitstrings_blocks_from_ci_yaml(text)
        link = _source_code_link(blocks[0], scan_path=ci)
        assert "Source:" in link
        assert "/-/blob/" in link

    def test_read_origin_url_from_config(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        config = git_dir / "config"
        parser = ConfigParser()
        parser.add_section('remote "origin"')
        parser.set('remote "origin"', "url", "https://gitlab.com/g/r.git")
        with config.open("w", encoding="utf-8") as handle:
            parser.write(handle)
        assert _read_origin_url(git_dir) == "https://gitlab.com/g/r.git"

    def test_read_head_ref_branch(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        assert _read_head_ref(git_dir) == "main"

    def test_read_head_ref_detached(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("abc123\n", encoding="utf-8")
        assert _read_head_ref(git_dir) == "abc123"

    def test_git_ref_prefers_ci_env(self, monkeypatch):
        monkeypatch.setenv("CI_COMMIT_SHA", "deadbeef")
        assert _git_ref(None, prefer_ci_ref=True) == "deadbeef"

    def test_repo_url_without_credentials(self):
        assert (
            _repo_url_without_credentials("git@gitlab.com:group/proj.git")
            == "https://gitlab.com/group/proj"
        )
        assert (
            _repo_url_without_credentials("https://user:tok@gitlab.com/g/r.git")
            == "https://gitlab.com/g/r"
        )

    def test_blob_url_gitlab_multiline(self):
        url = _blob_url(
            "https://gitlab.com/g/r",
            ref="main",
            relative_path="ci.yml",
            start_line=2,
            end_line=5,
        )
        assert "/-/blob/" in url
        assert "L2-5" in url

    def test_blob_url_github_style(self):
        url = _blob_url(
            "https://github.com/o/r",
            ref="main",
            relative_path="file.yml",
            start_line=1,
            end_line=3,
        )
        assert "/blob/" in url
        assert "L1-L3" in url

    def test_source_repository_url_ci(self, monkeypatch):
        monkeypatch.setenv("CI_REPOSITORY_URL", "https://gitlab.com/ci/proj")
        url, root, git_dir, prefer = _source_repository_url(REPO_ROOT / "x.yml")
        assert url == "https://gitlab.com/ci/proj"
        assert prefer is True


class TestGitstringsYamlAndRender:
    def test_load_yaml_root_multi_document_merge(self):
        text = "---\nspec:\n  inputs:\n    x: 1\n---\nvariables:\n  A: b\n"
        root = _load_yaml_root(text)
        assert root["variables"]["A"] == "b"
        assert root["spec"]["inputs"]["x"] == 1

    def test_load_yaml_root_non_dict_documents(self):
        root = _load_yaml_root("---\n- one\n---\n- two\n")
        assert "documents" in root

    def test_detect_render_mode_jobs_and_path(self):
        jobs_doc = {"build": {"stage": "test", "script": ["echo"]}}
        assert detect_render_mode(jobs_doc, "auto") == "jobs"
        assert detect_render_mode(jobs_doc, "build.stage") == "path"
        assert detect_render_mode({"spec": {"inputs": {"x": {}}}}, "auto") == "inputs"
        assert detect_render_mode({"variables": {"A": "1"}}, "auto") == "variables"
        assert (
            detect_render_mode({"include": [{"local": "x.yml"}]}, "auto") == "includes"
        )

    def test_looks_like_jobs_map_false(self):
        assert _looks_like_jobs_map({"x": "str"}) is False

    def test_limited_render_note_with_variables(self):
        root = {"JOB": {"variables": {"A": "1", "B": "2"}}}
        note = _limited_render_note(root, "JOB.variables.A")
        assert "Limited render" in note
        assert "Selected variable count" in note

    def test_limited_render_note_legacy_mode_empty(self):
        assert _limited_render_note({}, "variables") == ""
        assert _limited_render_note({}, "auto") == ""

    def test_count_variables_for_path_branches(self):
        root = {"job": {"variables": {"A": "1", "B": "2"}}, "variables": {"X": "y"}}
        assert _count_variables_for_path(root, "variables") == 1
        assert _count_variables_for_path(root, "job.variables") == 2
        assert _count_variables_for_path(root, "job.variables.A") == 1
        assert _count_variables_for_path(root, "missing") == 0

    def test_normalize_legacy_include_alias(self):
        assert normalize_legacy_render("include") == "includes"

    def test_resolve_fragment_output_honor_false(self, tmp_path):
        directives = GitstringsDirectives(output="other.md")
        target = resolve_fragment_output(
            directives,
            tmp_path / "out.md",
            tmp_path / "scan.md",
            honor_fragment_output=False,
        )
        assert target == (tmp_path / "out.md").resolve()

    def test_process_gitstrings_no_blocks(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("# no fences\n", encoding="utf-8")
        assert process_gitstrings(empty) == []

    def test_write_gitstrings_block_dry(self, tmp_path):
        target = tmp_path / "out.md"
        target.write_text(MARKER_BLOCK, encoding="utf-8")
        write_gitstrings_block(target, "content", dry=True)
        assert "content" not in target.read_text(encoding="utf-8")

    def test_render_fragment_source_link(self, tmp_path):
        ci = tmp_path / ".gitlab-ci.yml"
        ci.write_text(
            """# @title T
# @render variables
variables:
  X: 1
""",
            encoding="utf-8",
        )
        text = ci.read_text(encoding="utf-8")
        blocks = gs.extract_gitstrings_blocks_from_ci_yaml(text)
        out = render_fragment(
            blocks[0],
            keep_source=False,
            scan_path=ci,
            output_path=tmp_path / "README.md",
        )
        assert "Source:" in out or "variables" in out

    def test_load_pipeline_root_yaml_error(self, tmp_path, monkeypatch):
        bad = tmp_path / "bad.yml"
        bad.write_text(":\n  bad\n  yaml", encoding="utf-8")
        with patch.object(gs, "_load_yaml_root", side_effect=yaml.YAMLError("bad")):
            loaded = gs._load_pipeline_root(bad, {"fallback": True})
        assert loaded == {"fallback": True}

    def test_extract_blocks_from_ci_yaml_file(self, tmp_path):
        ci = tmp_path / ".gitlab-ci.yml"
        ci.write_text("# @render variables\nvariables:\n  Z: 1\n", encoding="utf-8")
        blocks = extract_gitstrings_blocks_from_file(ci)
        assert len(blocks) == 1

    def test_upgrade_legacy_gitstrings_markers(self, tmp_path):
        path = tmp_path / "README.md"
        path.write_text(
            f"{GITSTRINGS_MARKER_OPEN_LEGACY}\nold\n{GITSTRINGS_MARKER_CLOSE_LEGACY}\n",
            encoding="utf-8",
        )
        _upgrade_legacy_gitstrings_markers(path)
        text = path.read_text(encoding="utf-8")
        assert GITSTRINGS_MARKER_OPEN in text
        assert GITSTRINGS_MARKER_CLOSE in text

    def test_render_gitstrings_by_output_groups_fragments(self, tmp_path):
        ci = tmp_path / ".gitlab-ci.yml"
        ci.write_text(
            """# @render variables
variables:
  A: 1
# @output other.md
# @render variables
variables:
  B: 2
""",
            encoding="utf-8",
        )
        blocks = extract_gitstrings_blocks_from_file(ci)
        out = tmp_path / "README.md"
        out.write_text(MARKER_BLOCK, encoding="utf-8")
        (tmp_path / "other.md").write_text(MARKER_BLOCK, encoding="utf-8")
        grouped = render_gitstrings_by_output(
            blocks,
            default_output_path=out,
            scan_path=ci,
            keep_source=False,
            honor_fragment_output=True,
        )
        assert len(grouped) == 2


class TestTableRenderCoverage:
    def test_render_rules_table_workflow_and_scalar_rule(self):
        md = tr.render_rules_table(
            [{"if": "$CI"}, "when: never"],
            context="workflow",
        )
        assert "Workflow rules" in md
        assert "|" in md

    def test_render_path_workflow_and_rules(self):
        pipeline = {
            "workflow": {"rules": [{"if": "$CI_COMMIT_BRANCH"}]},
            "build": {
                "stage": "test",
                "rules": [{"if": "$CI", "when": "on_success"}],
            },
        }
        wf = tr.render_path_markdown(pipeline, "workflow")
        assert "Workflow rules" in wf
        rules = tr.render_path_markdown(pipeline, "build.rules")
        assert "Job rules" in rules

    def test_render_jobs_table_valid_job(self):
        md = tr.render_jobs_table(
            {"build": {"stage": "test", "script": ["echo hi"]}}
        )
        assert "build" in md
        assert "|" in md

    def test_render_includes_table_parsed_entries(self):
        md = tr.render_includes_table(
            parsed_entries=[
                {
                    "include_type": "local",
                    "project": "",
                    "version": "",
                    "valid_version": True,
                    "file": "child.yml",
                    "variables": {},
                    "rules": [],
                }
            ]
        )
        assert "child.yml" in md

    def test_render_includes_scalar_entry(self):
        md = tr.render_includes_table([{"local": "only.yml"}], config_file="ci.yml")
        assert "only.yml" in md

    def test_render_path_spec_inputs_and_job_segment(self):
        pipeline = {
            "spec": {"inputs": {"env": {"default": "prod", "description": "d"}}},
            "deploy": {"stage": "deploy", "script": ["./go"]},
        }
        inputs_md = tr.render_path_markdown(pipeline, "spec.inputs")
        assert "env" in inputs_md
        job_md = tr.render_path_markdown(pipeline, "deploy")
        assert "deploy" in job_md

    def test_render_path_workflow_with_extra_keys(self):
        pipeline = {
            "workflow": {
                "name": "main",
                "rules": [{"if": "$CI"}],
            }
        }
        md = tr.render_path_markdown(pipeline, "workflow")
        assert "Workflow rules" in md
        assert "name" in md

    def test_render_path_include_nested(self, tmp_path):
        ci = tmp_path / ".gitlab-ci.yml"
        ci.write_text(
            "include:\n  - local: child.yml\nchild:\n  script: echo\n",
            encoding="utf-8",
        )
        (tmp_path / "child.yml").write_text("variables:\n  X: 1\n", encoding="utf-8")
        root = yaml.safe_load(ci.read_text(encoding="utf-8"))
        md = tr.render_path_markdown(
            root,
            "include",
            include_nested=True,
            scan_path=ci,
        )
        assert "local" in md

    def test_render_includes_table_empty(self):
        assert tr.render_includes_table([]) == "_No includes defined._"

    def test_render_includes_from_config(self):
        md = tr.render_includes_from_config(str(SAMPLE), include_nested=False)
        assert "|" in md

    def test_render_path_missing_node(self):
        assert tr.render_path_markdown({}, "missing.path") == ""

    def test_render_generic_kv_sensitive_mask(self):
        md = tr.render_generic_kv_table(
            {"secret": "value"},
            path_prefix="job",
            sensitive_paths=["job.secret"],
        )
        assert "****" in md

    def test_inputs_row_metadata_error_path(self):
        class Evil(dict):
            def __getitem__(self, key):
                if key == "description":
                    raise RuntimeError("boom")
                return super().__getitem__(key)

        table = tr.render_inputs_table(
            {"k": Evil({"description": "x", "default": "d"})}
        )
        assert "k" in table

    def test_render_path_specs_comma_paths(self):
        root = {"spec": {"inputs": {"a": {"default": "1"}}}, "variables": {"b": "2"}}
        md = _render_path_specs(root, "spec.inputs, variables")
        assert "a" in md
        assert "b" in md

    def test_component_include_invalid_skipped(self):
        md = tr.render_includes_table([{"component": "bad-no-at"}])
        assert md == "_No includes defined._"


class TestDocumentGitstringsCli:
    def test_cli_include_nested_flag(self, tmp_path):
        from click.testing import CliRunner

        from src.gitlab_compliance import gitlab_compliance

        ci = tmp_path / ".gitlab-ci.yml"
        readme = tmp_path / "README.md"
        ci.write_text(
            """# @render includes
include:
  - local: x.yml
""",
            encoding="utf-8",
        )
        (tmp_path / "x.yml").write_text("variables:\n  Z: 1\n", encoding="utf-8")
        readme.write_text(MARKER_BLOCK, encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(
            gitlab_compliance,
            [
                "document",
                "gitstrings",
                "-i",
                str(ci),
                "-o",
                str(readme),
                "--include-nested",
                "--no-keep-source",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "local" in readme.read_text(encoding="utf-8")

    def test_process_gitstrings_dry_mode(self, tmp_path):
        readme = tmp_path / "r.md"
        before = (
            """```yaml gitstrings
# @render variables
variables:
  A: 1
```
"""
            + MARKER_BLOCK
        )
        readme.write_text(before, encoding="utf-8")
        written = process_gitstrings(readme, readme, dry=True, keep_source=False)
        assert len(written) == 1
        assert readme.read_text(encoding="utf-8") == before

    def test_render_table_or_list_empty_rows(self):
        from src.modules.common import render_table_or_list

        assert render_table_or_list(["Key"], []) == ""

    def test_swagger_markdown_with_pipeline_data(self):
        from src.modules.pipeline_data import collect_pipeline_data
        from src.modules.swagger_markdown import render_swagger_markdown

        data = collect_pipeline_data(str(SAMPLE), detailed=True)
        md = render_swagger_markdown(data)
        assert "## Includes" in md
        assert "|" in md

    def test_swagger_markdown_exclude_jobs(self):
        from src.modules.pipeline_data import collect_pipeline_data
        from src.modules.swagger_markdown import render_swagger_markdown

        data = collect_pipeline_data(
            str(SAMPLE),
            detailed=True,
            exclude_sections={"jobs"},
        )
        md = render_swagger_markdown(data)
        assert "## Jobs" not in md

    def test_swagger_markdown_grouped_jobs_and_workflow(self):
        from src.modules.pipeline_data import collect_pipeline_data
        from src.modules.swagger_markdown import render_swagger_markdown

        data = collect_pipeline_data(str(SAMPLE), detailed=True, group_by="stage")
        md = render_swagger_markdown(data)
        assert "## Workflow" in md or "_No" in md
        assert "Stage" in md or "## Jobs" in md

    def test_yaml_paths_parse_path_list(self):
        from src.properties.yaml_paths import parse_path_list

        assert parse_path_list("a, b , c") == ["a", "b", "c"]


class TestBehaveStepsSmoke:
    """Exercise step definitions without running full BDD scenarios."""

    def _ctx(self, stash):
        return SimpleNamespace(stash=stash, scenario_skipped=False, step_mode=None)

    def test_then_steps_with_patched_assert_all(self):
        from src.compliance.behave_support.steps import then_steps, when_steps

        entity = {"name": "job-a", "values": {"stage": "test", "script": "echo"}}
        context = self._ctx([entity])
        with patch.object(then_steps, "assert_all", MagicMock()):
            then_steps.then_must_contain(context, "stage")
            then_steps.then_must_not_contain(context, "missing")
            then_steps.then_property_must_be(context, "stage", "test")
            then_steps.then_property_must_match(context, "stage", "te.*")
            then_steps.then_property_must_not_match(context, "stage", "prod")
            then_steps.then_property_not_null(context, "stage")
            then_steps.then_extends_includes(context, ".base")
            then_steps.then_version_valid_semver(context)
            then_steps.then_no_newer_release(context)
            then_steps.then_no_newer_release_beyond_grace_days(context, 30)
            then_steps.then_release_lag_must_not_exceed_days(context, 7)
            then_steps.then_must_be_within_latest_tags(context, 3)
            then_steps.then_must_use_sha256_digest(context)
            then_steps.then_no_newer_image_release(context)
            then_steps.then_no_newer_image_release_beyond_grace_days(context, 14)
            then_steps.then_image_release_lag_must_not_exceed_days(context, 7)
            then_steps.then_must_be_within_latest_image_tags(context, 5)
            then_steps.then_version_is_latest_release(context)

        with patch.object(when_steps, "filter_entities", return_value=[entity]):
            when_steps.when_it_has(context, "stage")
            when_steps.when_it_does_not_have(context, "missing")
            when_steps.when_property_is(context, "stage", "test")
            when_steps.when_property_matches(context, "stage", "te.*")
            when_steps.when_input_is(context, "env", "prod")
            when_steps.when_name_not_starts_with(context, "zzz")
            when_steps.when_newer_release_available(context)
            when_steps.when_newer_release_available_for_more_than_days(context, 30)
            when_steps.when_release_lag_exceeds_days(context, 7)
            when_steps.when_not_within_latest_tags(context, 3)
            when_steps.when_newer_image_release_available(context)
            when_steps.when_newer_image_release_available_for_more_than_days(
                context, 14
            )
            when_steps.when_image_release_lag_exceeds_days(context, 7)
            when_steps.when_not_within_latest_image_tags(context, 5)
