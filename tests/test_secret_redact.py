"""Tests for secret redaction and CI_JOB_TOKEN gating."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.compliance import secret_redact as sr
from src.compliance.merge_requests import (
    create_supply_chain_merge_request,
    post_compliance_mr_comment,
)
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.render import render_compliance_mr_comment
from src.compliance.runner import run_compliance

PASSING_POLICIES = Path(__file__).resolve().parent / "compliance_policies" / "passing"
SAMPLE_PIPELINE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "sample-files"
    / ".gitlab-ci.yml"
)


class TestRedactSecrets:
    def test_redacts_glpat_pattern(self):
        token = "glpat-" + ("a" * 20)
        assert sr.REDACTED in sr.redact_secrets(f"error with {token} embedded")
        assert token not in sr.redact_secrets(f"error with {token} embedded")

    def test_redacts_env_secret_values(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "super-secret-token-value")
        text = sr.redact_secrets("failed using super-secret-token-value for API")
        assert "super-secret-token-value" not in text
        assert sr.REDACTED in text

    def test_redacts_private_token_query(self):
        text = sr.redact_secrets(
            "https://gitlab.example.com/api?private_token=abc123456789"
        )
        assert "abc123456789" not in text
        assert "private_token=" in text
        assert sr.REDACTED in text

    def test_empty_and_none(self):
        assert sr.redact_secrets("") == ""
        assert sr.redact_secrets(None) == ""

    def test_token_is_ci_job_token(self, monkeypatch):
        monkeypatch.setenv("CI_JOB_TOKEN", "job-token-value-here")
        assert sr.token_is_ci_job_token("job-token-value-here") is True
        assert sr.token_is_ci_job_token("other") is False


class TestMrCommentRedaction:
    def test_render_mr_comment_redacts_scenario_message(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "leak-me-please-token")
        result = ComplianceResult(
            success=False,
            exit_code=1,
            failed=1,
            scenario_results=[
                ScenarioResult(
                    feature="a.feature",
                    name="fail",
                    status="failed",
                    policy_id="P-1",
                    title="Fail",
                    message="boom leak-me-please-token boom",
                )
            ],
        )
        comment = render_compliance_mr_comment(result, "ci.yml", "policies/")
        assert "leak-me-please-token" not in comment
        assert sr.REDACTED in comment

    def test_post_comment_redacts_file_body(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "file-secret-token-xx")
        project_obj = MagicMock()
        merge_request = MagicMock()
        project_obj.mergerequests.get.return_value = merge_request
        gl = MagicMock()
        gl.projects.get.return_value = project_obj
        with patch("src.compliance.merge_requests.gitlab.Gitlab", return_value=gl):
            post_compliance_mr_comment(
                body="note with file-secret-token-xx inside",
                gitlab_url="https://gitlab.example.com",
                token="ok-token",
                project="group/proj",
                mr_iid=7,
            )
        body = merge_request.notes.create.call_args[0][0]["body"]
        assert "file-secret-token-xx" not in body
        assert sr.REDACTED in body


class TestCreateMrRejectsCiJobToken:
    def test_create_mr_helper_rejects_ci_job_token(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CI_JOB_TOKEN", "ci-job-token-secret")
        fixed = tmp_path / "pipeline.yml"
        fixed.write_text("x: 1\n", encoding="utf-8")
        with pytest.raises(ValueError, match="does not accept CI_JOB_TOKEN"):
            create_supply_chain_merge_request(
                pipeline_file=str(fixed),
                fix_messages=[f"Fixed include x: 1 -> 2 ({fixed}:1)"],
                gitlab_url="https://gitlab.example.com",
                token="ci-job-token-secret",
                project="group/proj",
            )

    def test_run_compliance_rejects_ci_job_token_for_create_mr(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.setenv("CI_JOB_TOKEN", "ci-job-token-secret")
        with pytest.raises(ValueError, match="does not accept CI_JOB_TOKEN"):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                create_mr=True,
                token="",
                project="group/proj",
            )
