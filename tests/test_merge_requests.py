"""Tests for GitLab merge request helpers and check flag gating."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.compliance import merge_requests as mr
from src.compliance.runner import run_compliance

SAMPLE_PIPELINE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "sample-files"
    / ".gitlab-ci.yml"
)
PASSING_POLICIES = Path(__file__).resolve().parent / "compliance_policies" / "passing"


def _project_mock(
    *,
    branch_exists: bool = True,
    opened=None,
    closed=None,
    file_exists: bool = True,
):
    project_obj = MagicMock()
    project_obj.default_branch = "main"
    project_obj.web_url = "https://gitlab.example.com/group/proj"
    if branch_exists:
        project_obj.branches.get.return_value = MagicMock()
    else:
        project_obj.branches.get.side_effect = mr.gitlab.exceptions.GitlabGetError(
            response_code=404, error_message="not found"
        )

    if file_exists:
        project_obj.files.get.return_value = MagicMock()
    else:
        project_obj.files.get.side_effect = mr.gitlab.exceptions.GitlabGetError(
            response_code=404, error_message="not found"
        )

    opened_list = list(opened or [])
    closed_list = list(closed or [])

    def _list_mrs(**kwargs):
        state = kwargs.get("state")
        if state == "opened":
            return opened_list
        if state == "closed":
            return closed_list
        return []

    project_obj.mergerequests.list.side_effect = _list_mrs
    return project_obj


class TestMrDescription:
    def test_description_with_changes(self):
        body = mr._mr_description(
            ["Fixed include x: 1 -> 2 (a.yml:1)"],
            files_updated=1,
        )
        assert "Supply-chain compliance fix" in body
        assert "1. Fixed include" in body
        assert "Files updated | `1`" in body

    def test_description_without_change_details(self):
        body = mr._mr_description([], files_updated=0)
        assert "_No change details were recorded._" in body
        assert "Review notes" in body


class TestChangedFilesFromFixMessages:
    def test_extracts_unique_paths(self):
        messages = [
            "Fixed include platform/ci: 1.0.0 -> 1.1.0 (ci/child.yml:3)",
            "Fixed image alpine:3 -> alpine@sha256:abc (job build, ci/child.yml:10)",
            "Fixed include other: 1 -> 2 (/tmp/other.yml:1)",
            "no path here",
            "Fixed include empty: 1 -> 2 (:2)",
        ]
        assert mr._changed_files_from_fix_messages(messages) == [
            "ci/child.yml",
            "/tmp/other.yml",
        ]

    def test_skips_blank_path_group(self):
        # Path group can be whitespace-only after strip → skipped by `if path`
        assert mr._changed_files_from_fix_messages(["note (   :3)"]) == []


class TestRepoRelativePath:
    def test_relative_to_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("CI_PROJECT_DIR", raising=False)
        nested = tmp_path / "ci" / "file.yml"
        nested.parent.mkdir()
        nested.write_text("x\n", encoding="utf-8")
        assert mr._repo_relative_path(str(nested), str(nested)) == "ci/file.yml"

    def test_relative_to_ci_project_dir(self, tmp_path, monkeypatch):
        root = tmp_path / "repo"
        root.mkdir()
        file_path = root / "a.yml"
        file_path.write_text("x\n", encoding="utf-8")
        monkeypatch.setenv("CI_PROJECT_DIR", str(root))
        assert mr._repo_relative_path(str(file_path), str(file_path)) == "a.yml"

    def test_fallback_when_outside_roots(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("CI_PROJECT_DIR", raising=False)
        outside = tmp_path / "outside.yml"
        # Force commonpath failure by using a nonsense absolute that won't nest
        with patch(
            "src.compliance.merge_requests.os.path.commonpath", side_effect=ValueError
        ):
            result = mr._repo_relative_path(str(outside), str(tmp_path / "ci.yml"))
        assert result.endswith("outside.yml")


class TestResolveHelpers:
    def test_resolve_gitlab_url_precedence(self, monkeypatch):
        monkeypatch.delenv("CI_SERVER_URL", raising=False)
        monkeypatch.delenv("GITLAB_URL", raising=False)
        assert mr._resolve_gitlab_url("https://custom") == "https://custom"
        assert mr._resolve_gitlab_url(None) == "https://gitlab.com"
        monkeypatch.setenv("GITLAB_URL", "https://from-env")
        assert mr._resolve_gitlab_url(None) == "https://from-env"
        monkeypatch.setenv("CI_SERVER_URL", "https://ci")
        assert mr._resolve_gitlab_url(None) == "https://ci"

    def test_resolve_project_path_missing(self, monkeypatch):
        monkeypatch.delenv("CI_PROJECT_PATH", raising=False)
        with patch("src.compliance.merge_requests.resolve_project", return_value=None):
            with pytest.raises(ValueError, match="GitLab project is required"):
                mr._resolve_project_path(None)

    def test_default_branch_name_is_stable(self):
        assert mr._default_branch_name() == "gitlab-compliance/supply-chain-fix"
        assert mr._default_branch_name() == mr._DEFAULT_SOURCE_BRANCH

    def test_friendly_gitlab_error_empty_message(self):
        class Empty(Exception):
            def __str__(self):
                return ""

        err = mr._friendly_gitlab_error(Empty(), action="testing")
        assert "GitLab API error while testing" in str(err)
        assert "Empty" in str(err)


class TestCreateSupplyChainMergeRequest:
    def test_requires_token(self):
        with pytest.raises(ValueError, match="--create-mr requires a GitLab token"):
            mr.create_supply_chain_merge_request(
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_messages=["Fixed include x: 1 -> 2 (a.yml:1)"],
                gitlab_url="https://gitlab.example.com",
                token="",
                project="group/proj",
            )

    def test_skips_when_no_changed_files(self):
        url = mr.create_supply_chain_merge_request(
            pipeline_file=str(SAMPLE_PIPELINE),
            fix_messages=[],
            gitlab_url="https://gitlab.example.com",
            token="token",
            project="group/proj",
        )
        assert url is None

    def test_creates_branch_commit_and_mr(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("include:\n  - project: x\n    ref: 2.0.0\n", encoding="utf-8")
        messages = [f"Fixed include x: 1.0.0 -> 2.0.0 ({fixed}:2)"]

        project_obj = _project_mock(branch_exists=False)
        merge_request = MagicMock()
        merge_request.web_url = (
            "https://gitlab.example.com/group/proj/-/merge_requests/9"
        )
        merge_request.iid = 9
        project_obj.mergerequests.create.return_value = merge_request

        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/supply-chain",
                target_branch="main",
            )

        assert url.endswith("/merge_requests/9")
        project_obj.branches.create.assert_called_once()
        project_obj.commits.create.assert_called_once()
        project_obj.mergerequests.create.assert_called_once()

    def test_uses_default_branch_name_and_project_default_target(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1.0.0 -> 2.0.0 ({fixed}:1)"]
        project_obj = _project_mock(branch_exists=True)
        merge_request = MagicMock()
        merge_request.web_url = ""
        merge_request.iid = 3
        project_obj.mergerequests.create.return_value = merge_request
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url=None,
                token="token",
                project="group/proj",
            )

        assert url == "3"
        commit_kwargs = project_obj.commits.create.call_args[0][0]
        assert commit_kwargs["branch"] == "gitlab-compliance/supply-chain-fix"
        assert project_obj.mergerequests.list.call_count == 2
        create_kwargs = project_obj.mergerequests.create.call_args[0][0]
        assert create_kwargs["target_branch"] == "main"
        assert create_kwargs["title"] == mr._MR_TITLE
        assert "Supply-chain compliance fix" in create_kwargs["description"]
        assert "### Changes" in create_kwargs["description"]

    def test_updates_existing_merge_request(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("include:\n  - project: x\n    ref: 2.0.0\n", encoding="utf-8")
        messages = [f"Fixed include x: 1.0.0 -> 2.0.0 ({fixed}:2)"]

        merge_request = MagicMock()
        merge_request.web_url = (
            "https://gitlab.example.com/group/proj/-/merge_requests/9"
        )
        project_obj = _project_mock(opened=[merge_request])

        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/supply-chain",
                target_branch="main",
            )

        assert url.endswith("/merge_requests/9")
        project_obj.mergerequests.create.assert_not_called()
        project_obj.commits.create.assert_called_once()
        assert "### Changes" in merge_request.description
        assert "Supply-chain compliance fix" in merge_request.description
        assert getattr(merge_request, "state_event", None) != "reopen"
        merge_request.save.assert_called_once()

    def test_reopens_closed_merge_request(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        closed_mr = MagicMock()
        closed_mr.web_url = "https://gitlab.example.com/group/proj/-/merge_requests/11"
        closed_mr.iid = 11
        project_obj = _project_mock(branch_exists=True, closed=[closed_mr])
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/supply-chain",
            )

        assert url.endswith("/merge_requests/11")
        assert closed_mr.state_event == "reopen"
        assert closed_mr.title == mr._MR_TITLE
        closed_mr.save.assert_called_once()
        project_obj.mergerequests.create.assert_not_called()

    def test_reopens_most_recently_updated_closed_mr(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        older = MagicMock()
        older.web_url = "https://gitlab.example.com/group/proj/-/merge_requests/10"
        older.iid = 10
        older.updated_at = "2024-01-01T00:00:00Z"
        newer = MagicMock()
        newer.web_url = "https://gitlab.example.com/group/proj/-/merge_requests/12"
        newer.iid = 12
        newer.updated_at = "2025-06-01T00:00:00Z"
        project_obj = _project_mock(branch_exists=True, closed=[older, newer])
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/supply-chain",
            )

        assert url.endswith("/merge_requests/12")
        assert newer.state_event == "reopen"
        older.save.assert_not_called()

    def test_commit_uses_create_when_file_missing_on_branch(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        project_obj = _project_mock(branch_exists=True, file_exists=False)
        merge_request = MagicMock()
        merge_request.web_url = (
            "https://gitlab.example.com/group/proj/-/merge_requests/1"
        )
        merge_request.iid = 1
        project_obj.mergerequests.create.return_value = merge_request
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/new-file",
            )

        actions = project_obj.commits.create.call_args[0][0]["actions"]
        assert actions[0]["action"] == "create"

    def test_commit_failure_after_new_branch_mentions_orphan_risk(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        project_obj = _project_mock(branch_exists=False)
        project_obj.commits.create.side_effect = mr.gitlab.exceptions.GitlabError(
            "commit denied"
        )
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            with pytest.raises(
                ValueError,
                match=r"newly created branch `fix/orphan`.*delete `fix/orphan`",
            ):
                mr.create_supply_chain_merge_request(
                    pipeline_file=str(fixed),
                    fix_messages=messages,
                    gitlab_url="https://gitlab.example.com",
                    token="token",
                    project="group/proj",
                    branch_name="fix/orphan",
                )
        project_obj.branches.create.assert_called_once()

    def test_updates_existing_mr_without_web_url(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        merge_request = MagicMock()
        merge_request.web_url = ""
        merge_request.iid = 42
        project_obj = _project_mock(opened=[merge_request])
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/b",
            )
        assert url == "42"
        merge_request.save.assert_called_once()
        project_obj.mergerequests.create.assert_not_called()

    def test_checks_for_existing_mr_before_creating(self, tmp_path):
        """Re-runs on the stable default branch must not open a second MR."""
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        existing = MagicMock()
        existing.web_url = "https://gitlab.example.com/group/proj/-/merge_requests/5"
        existing.iid = 5
        project_obj = _project_mock(branch_exists=True, opened=[existing])
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            first = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
            )
            second = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages + [f"Fixed include y: 1 -> 2 ({fixed}:1)"],
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
            )

        assert first == second == existing.web_url
        assert project_obj.mergerequests.create.call_count == 0
        assert project_obj.commits.create.call_count == 2
        assert existing.save.call_count == 2
        assert project_obj.mergerequests.list.call_count >= 2
        for call in project_obj.mergerequests.list.call_args_list:
            assert call.kwargs["source_branch"] == "gitlab-compliance/supply-chain-fix"

    def test_skips_missing_files_then_no_actions(self, tmp_path):
        missing = tmp_path / "gone.yml"
        messages = [f"Fixed include x: 1 -> 2 ({missing}:1)"]
        url = mr.create_supply_chain_merge_request(
            pipeline_file=str(tmp_path / "root.yml"),
            fix_messages=messages,
            gitlab_url="https://gitlab.example.com",
            token="token",
            project="group/proj",
        )
        assert url is None

    def test_skips_missing_file_but_commits_existing(self, tmp_path):
        missing = tmp_path / "gone.yml"
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [
            f"Fixed include x: 1 -> 2 ({missing}:1)",
            f"Fixed include y: 1 -> 2 ({fixed}:1)",
        ]
        project_obj = _project_mock(branch_exists=True)
        merge_request = MagicMock()
        merge_request.web_url = "https://gitlab.example.com/mr/1"
        merge_request.iid = 1
        project_obj.mergerequests.create.return_value = merge_request
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            url = mr.create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=messages,
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                branch_name="fix/b",
            )

        assert url.endswith("/mr/1")
        actions = project_obj.commits.create.call_args[0][0]["actions"]
        assert len(actions) == 1
        assert actions[0]["file_path"].endswith("pipeline.yml")

    def test_wraps_gitlab_api_errors(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        gl = MagicMock()
        gl.projects.get.side_effect = mr.gitlab.exceptions.GitlabError("denied")

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            with pytest.raises(ValueError, match="GitLab API error while creating"):
                mr.create_supply_chain_merge_request(
                    pipeline_file=str(fixed),
                    fix_messages=messages,
                    gitlab_url="https://gitlab.example.com",
                    token="token",
                    project="group/proj",
                )

    def test_mr_create_failure_after_commit_mentions_branch(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        project_obj = _project_mock(branch_exists=True)
        project_obj.mergerequests.create.side_effect = mr.gitlab.exceptions.GitlabError(
            "cannot create"
        )
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            with pytest.raises(
                ValueError,
                match=r"after committing to `fix/orphan`.*open or repair the MR",
            ):
                mr.create_supply_chain_merge_request(
                    pipeline_file=str(fixed),
                    fix_messages=messages,
                    gitlab_url="https://gitlab.example.com",
                    token="token",
                    project="group/proj",
                    branch_name="fix/orphan",
                )
        project_obj.commits.create.assert_called_once()

    def test_mr_update_failure_after_commit_mentions_branch(self, tmp_path):
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        messages = [f"Fixed include x: 1 -> 2 ({fixed}:1)"]
        existing = MagicMock()
        existing.web_url = "https://gitlab.example.com/mr/9"
        existing.iid = 9
        existing.save.side_effect = mr.gitlab.exceptions.GitlabError("cannot save")
        project_obj = _project_mock(opened=[existing])
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            with pytest.raises(
                ValueError,
                match=r"after committing to `fix/b`.*refresh the MR",
            ):
                mr.create_supply_chain_merge_request(
                    pipeline_file=str(fixed),
                    fix_messages=messages,
                    gitlab_url="https://gitlab.example.com",
                    token="token",
                    project="group/proj",
                    branch_name="fix/b",
                )
        project_obj.commits.create.assert_called_once()


class TestPostComplianceMrComment:
    def test_requires_token(self):
        with pytest.raises(
            ValueError, match="--post-mr-comment requires a GitLab token"
        ):
            mr.post_compliance_mr_comment(
                body="hello",
                gitlab_url="https://gitlab.example.com",
                token="",
                project="group/proj",
                mr_iid=1,
            )

    def test_requires_mr_iid(self, monkeypatch):
        monkeypatch.delenv("CI_MERGE_REQUEST_IID", raising=False)
        with pytest.raises(ValueError, match="--mr-iid"):
            mr.post_compliance_mr_comment(
                body="hello",
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                mr_iid=None,
            )

    def test_ignores_non_digit_ci_iid(self, monkeypatch):
        monkeypatch.setenv("CI_MERGE_REQUEST_IID", "abc")
        with pytest.raises(ValueError, match="--mr-iid"):
            mr.post_compliance_mr_comment(
                body="hello",
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
                mr_iid=None,
            )

    def test_posts_note(self, monkeypatch):
        monkeypatch.setenv("CI_MERGE_REQUEST_IID", "12")
        project_obj = MagicMock()
        merge_request = MagicMock()
        project_obj.mergerequests.get.return_value = merge_request
        gl = MagicMock()
        gl.projects.get.return_value = project_obj

        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            mr.post_compliance_mr_comment(
                body="report body",
                gitlab_url="https://gitlab.example.com",
                token="token",
                project="group/proj",
            )

        project_obj.mergerequests.get.assert_called_once_with(12)
        merge_request.notes.create.assert_called_once_with({"body": "report body"})

    def test_wraps_gitlab_api_errors(self):
        gl = MagicMock()
        gl.projects.get.side_effect = mr.gitlab.exceptions.GitlabError("nope")
        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            with pytest.raises(ValueError, match="GitLab API error while posting"):
                mr.post_compliance_mr_comment(
                    body="x",
                    gitlab_url="https://gitlab.example.com",
                    token="token",
                    project="group/proj",
                    mr_iid=7,
                )


class TestRunComplianceMrFlags:
    def test_create_mr_requires_fix(self):
        with pytest.raises(
            ValueError,
            match="--create-mr requires --fix-supply-chain and/or --fix-policies",
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                create_mr=True,
                fix_supply_chain=False,
            )

    def test_create_mr_rejects_dry_run(self):
        with pytest.raises(
            ValueError, match="--create-mr cannot be used with --dry-run"
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                create_mr=True,
                fix_supply_chain=True,
                dry_run=True,
            )

    def test_create_mr_invokes_helper(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "secret")
        with (
            patch(
                "src.compliance.supply_chain_fix.apply_supply_chain_fixes",
                return_value=["Fixed include x: 1 -> 2 (ci.yml:1)"],
            ),
            patch(
                "src.compliance.merge_requests.create_supply_chain_merge_request"
            ) as create_mr,
            patch("src.compliance.runner.Runner") as mock_runner_cls,
        ):
            mock_runner_cls.return_value.run.return_value = 0
            mock_runner_cls.return_value.features = []
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                create_mr=True,
                token="secret",
                project="group/proj",
                mr_branch="fix/b",
                mr_target_branch="main",
                output_format="markdown",
            )
        assert result.success is True
        create_mr.assert_called_once()
        assert create_mr.call_args.kwargs["branch_name"] == "fix/b"

    def test_create_mr_failure_fails_process_after_report(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "secret")
        with (
            patch(
                "src.compliance.supply_chain_fix.apply_supply_chain_fixes",
                return_value=["Fixed include x: 1 -> 2 (ci.yml:1)"],
            ),
            patch(
                "src.compliance.merge_requests.create_supply_chain_merge_request",
                side_effect=ValueError("GitLab project is required"),
            ),
            patch("src.compliance.runner.print_error") as print_error,
            patch("src.compliance.runner.logger") as mock_logger,
            patch("src.compliance.runner.Runner") as mock_runner_cls,
        ):
            mock_runner_cls.return_value.run.return_value = 0
            mock_runner_cls.return_value.features = []
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                create_mr=True,
                token="secret",
                output_format="markdown",
            )
        assert result.success is False
        assert result.exit_code == 2
        assert mock_runner_cls.return_value.run.call_count == 1
        print_error.assert_called_once()
        assert "GitLab project is required" in print_error.call_args.args[0]
        mock_logger.error.assert_called()
        mock_logger.info.assert_called()

    def test_post_mr_comment_failure_fails_process_after_report(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "token")
        with (
            patch(
                "src.compliance.merge_requests.post_compliance_mr_comment",
                side_effect=ValueError("boom comment"),
            ),
            patch(
                "src.compliance.render.render_compliance_mr_comment",
                return_value="body",
            ),
            patch("src.compliance.runner.print_error") as print_error,
            patch("src.compliance.runner.logger") as mock_logger,
        ):
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                post_mr_comment=True,
                project="group/proj",
                mr_iid=3,
                output_format="markdown",
            )
        assert result.success is False
        assert result.exit_code == 2
        mock_logger.info.assert_called()
        mock_logger.error.assert_called()
        print_error.assert_called_once()
        assert "boom comment" in print_error.call_args.args[0]

    def test_post_mr_comment_uses_helper(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "token")
        with (
            patch(
                "src.compliance.merge_requests.post_compliance_mr_comment"
            ) as post_comment,
            patch(
                "src.compliance.render.render_compliance_mr_comment",
                return_value="body",
            ),
        ):
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                post_mr_comment=True,
                project="group/proj",
                mr_iid=3,
                output_format="markdown",
            )
        assert result.success is True
        post_comment.assert_called_once()
        assert post_comment.call_args.kwargs["mr_iid"] == 3
        assert post_comment.call_args.kwargs["body"] == "body"

    def test_post_mr_comment_reads_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "token")
        comment = tmp_path / "comment.md"
        comment.write_text("pre-rendered", encoding="utf-8")
        with patch(
            "src.compliance.merge_requests.post_compliance_mr_comment"
        ) as post_comment:
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                post_mr_comment=True,
                project="group/proj",
                mr_iid=3,
                mr_comment_file=str(comment),
                output_format="markdown",
            )
        assert post_comment.call_args.kwargs["body"] == "pre-rendered"
