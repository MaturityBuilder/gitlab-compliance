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


class TestChangedFilesFromFixMessages:
    def test_extracts_unique_paths(self):
        messages = [
            "Fixed include platform/ci: 1.0.0 -> 1.1.0 (ci/child.yml:3)",
            "Fixed image alpine:3 -> alpine@sha256:abc (job build, ci/child.yml:10)",
            "Fixed include other: 1 -> 2 (/tmp/other.yml:1)",
        ]
        assert mr._changed_files_from_fix_messages(messages) == [
            "ci/child.yml",
            "/tmp/other.yml",
        ]


class TestCreateSupplyChainMergeRequest:
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

        project_obj = MagicMock()
        project_obj.default_branch = "main"
        project_obj.branches.get.side_effect = mr.gitlab.exceptions.GitlabGetError(
            response_code=404, error_message="not found"
        )
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


class TestPostComplianceMrComment:
    def test_requires_mr_iid(self):
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


class TestRunComplianceMrFlags:
    def test_create_mr_requires_fix(self):
        with pytest.raises(ValueError, match="--create-mr requires --fix"):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                create_mr=True,
                fix=False,
            )

    def test_create_mr_rejects_dry_run(self):
        with pytest.raises(
            ValueError, match="--create-mr cannot be used with --dry-run"
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                create_mr=True,
                fix=True,
                dry_run=True,
            )

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
