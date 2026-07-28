"""Tests for allowlisted --fix-policies remediations."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.compliance import policy_fix as pf
from src.compliance.models import ScenarioResult
from src.compliance.runner import run_compliance

PASSING_POLICIES = Path(__file__).resolve().parent / "compliance_policies" / "passing"
SAMPLE_PIPELINE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "sample-files"
    / ".gitlab-ci.yml"
)


class TestPolicyFixRegistry:
    def test_supported_ids_cover_documented_remediations(self):
        ids = pf.supported_policy_ids()
        assert "GLCI-IMAGE-PINNING-001" in ids
        assert "GLCI-INCLUDE-VERSIONS-003" in ids
        assert "GLCI-INCLUDE-VERSIONS-001" not in ids

    def test_kind_lookup(self):
        assert (
            pf.remediation_kind_for_policy("GLCI-IMAGE-PINNING-001") == "image_digest"
        )
        assert (
            pf.remediation_kind_for_policy("GLCI-INCLUDE-VERSIONS-004")
            == "include_latest"
        )
        assert pf.remediation_kind_for_policy("UNKNOWN") is None


class TestApplyPolicyRemediations:
    def test_no_failures_is_noop(self):
        messages = pf.apply_policy_remediations(
            [ScenarioResult(feature="a.feature", name="ok", status="passed")],
            pipeline_file=str(SAMPLE_PIPELINE),
            token="token",
        )
        assert messages == []

    def test_unsupported_failure_warns_and_skips(self, monkeypatch):
        warnings: list[str] = []
        monkeypatch.setattr(
            pf, "print_warning", lambda message, **_kwargs: warnings.append(message)
        )
        monkeypatch.setattr(pf, "print_info", lambda *_a, **_k: None)
        messages = pf.apply_policy_remediations(
            [
                ScenarioResult(
                    feature="a.feature",
                    name="custom",
                    status="failed",
                    policy_id="CUSTOM-POLICY-1",
                    message="boom",
                )
            ],
            pipeline_file=str(SAMPLE_PIPELINE),
            token="token",
        )
        assert messages == []
        assert any("not auto-fixable" in item for item in warnings)

    def test_image_pinning_uses_container_fix(self, monkeypatch):
        applied = []
        source = str(SAMPLE_PIPELINE)

        def fake_collect(_entities):
            return [
                MagicMock(
                    source_file=source,
                    line=4,
                    current_image="alpine:3",
                    fixed_image="alpine@sha256:abc",
                    image_source="job",
                    parent_job="build",
                ),
                MagicMock(
                    source_file=source,
                    line=20,
                    current_image="redis:7",
                    fixed_image="redis@sha256:def",
                    image_source="service",
                    parent_job="build",
                ),
            ]

        def fake_apply(fixes):
            applied.extend(fixes)
            return list(fixes)

        entities = {
            "container_images": [
                {
                    "source_file": source,
                    "line": 4,
                    "image": "alpine:3",
                    "image_source": "job",
                    "parent_job": "build",
                    "latest_digest": "abc",
                },
                {
                    "source_file": source,
                    "line": 20,
                    "image": "redis:7",
                    "image_source": "service",
                    "parent_job": "build",
                    "latest_digest": "def",
                },
            ]
        }
        monkeypatch.setattr(pf, "load_pipeline_entities", lambda **_k: entities)
        monkeypatch.setattr(pf, "collect_container_image_fixes", fake_collect)
        monkeypatch.setattr(pf, "apply_container_image_fixes", fake_apply)
        monkeypatch.setattr(pf, "print_info", lambda *_a, **_k: None)
        monkeypatch.setattr(pf, "print_warning", lambda *_a, **_k: None)

        messages = pf.apply_policy_remediations(
            [
                ScenarioResult(
                    feature="image-pinning.feature",
                    name="pin",
                    status="failed",
                    policy_id="GLCI-IMAGE-PINNING-001",
                )
            ],
            pipeline_file=str(SAMPLE_PIPELINE),
            token="token",
        )
        assert len(messages) == 1
        assert "alpine@sha256:abc" in messages[0]
        assert "(job build," in messages[0]
        assert len(applied) == 1
        assert applied[0].line == 4

    def test_include_latest_scopes_to_failing_entities(self, monkeypatch):
        source = str(SAMPLE_PIPELINE)
        applied = []

        def fake_collect(_entities):
            return [
                MagicMock(
                    source_file=source,
                    line=2,
                    project="group/old",
                    current_version="1.0.0",
                    latest_version="1.2.0",
                ),
                MagicMock(
                    source_file=source,
                    line=8,
                    project="group/grace",
                    current_version="1.0.0",
                    latest_version="1.1.0",
                ),
            ]

        def fake_apply(fixes):
            applied.extend(fixes)
            return list(fixes)

        entities = {
            "includes": [
                {
                    "source_file": source,
                    "line": 2,
                    "project": "group/old",
                    "version": "1.0.0",
                    "latest_version": "1.2.0",
                    "update_available": True,
                    "latest_release_age_days": 45,
                    "release_lag_days": 40,
                    "release_metadata_resolved": True,
                    "version_tag_rank": 5,
                },
                {
                    "source_file": source,
                    "line": 8,
                    "project": "group/grace",
                    "version": "1.0.0",
                    "latest_version": "1.1.0",
                    "update_available": True,
                    "latest_release_age_days": 5,
                    "release_lag_days": 5,
                    "release_metadata_resolved": True,
                    "version_tag_rank": 2,
                },
            ]
        }
        monkeypatch.setattr(pf, "load_pipeline_entities", lambda **_k: entities)
        monkeypatch.setattr(pf, "collect_include_version_fixes", fake_collect)
        monkeypatch.setattr(pf, "apply_include_version_fixes", fake_apply)
        monkeypatch.setattr(pf, "print_info", lambda *_a, **_k: None)
        monkeypatch.setattr(pf, "print_warning", lambda *_a, **_k: None)

        messages = pf.apply_policy_remediations(
            [
                ScenarioResult(
                    feature="include-versions.feature",
                    name="grace",
                    status="failed",
                    policy_id="GLCI-INCLUDE-VERSIONS-004",
                )
            ],
            pipeline_file=str(SAMPLE_PIPELINE),
            token="token",
        )
        assert len(messages) == 1
        assert "group/old" in messages[0]
        assert len(applied) == 1
        assert applied[0].line == 2

    def test_include_latest_uses_include_fix(self, monkeypatch):
        source = str(SAMPLE_PIPELINE)

        def fake_collect(_entities):
            return [
                MagicMock(
                    source_file=source,
                    line=2,
                    project="group/ci",
                    current_version="1.0.0",
                    latest_version="1.2.0",
                )
            ]

        def fake_apply(fixes):
            return list(fixes)

        entities = {
            "includes": [
                {
                    "source_file": source,
                    "line": 2,
                    "project": "group/ci",
                    "version": "1.0.0",
                    "latest_version": "1.2.0",
                    "update_available": True,
                    "release_metadata_resolved": True,
                }
            ]
        }
        monkeypatch.setattr(pf, "load_pipeline_entities", lambda **_k: entities)
        monkeypatch.setattr(pf, "collect_include_version_fixes", fake_collect)
        monkeypatch.setattr(pf, "apply_include_version_fixes", fake_apply)
        monkeypatch.setattr(pf, "print_info", lambda *_a, **_k: None)
        monkeypatch.setattr(pf, "print_warning", lambda *_a, **_k: None)

        messages = pf.apply_policy_remediations(
            [
                ScenarioResult(
                    feature="include-versions.feature",
                    name="latest",
                    status="failed",
                    policy_id="GLCI-INCLUDE-VERSIONS-003",
                )
            ],
            pipeline_file=str(SAMPLE_PIPELINE),
            token="token",
        )
        assert messages == [f"Fixed include group/ci: 1.0.0 -> 1.2.0 ({source}:2)"]


class TestRunComplianceFixPolicies:
    def test_create_mr_accepts_fix_policies_only(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "secret")
        with (
            patch(
                "src.compliance.policy_fix.apply_policy_remediations",
                return_value=["Fixed include x: 1 -> 2 (ci.yml:1)"],
            ) as remediate,
            patch(
                "src.compliance.merge_requests.create_supply_chain_merge_request"
            ) as create_mr,
            patch("src.compliance.runner.Runner") as mock_runner_cls,
        ):
            mock_runner = mock_runner_cls.return_value
            mock_runner.run.return_value = 0
            mock_runner.features = []
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_policies=True,
                create_mr=True,
                token="secret",
                project="group/proj",
                output_format="markdown",
            )
        assert result.success is True
        assert remediate.called
        create_mr.assert_called_once()
        assert create_mr.call_args.kwargs["fix_messages"] == [
            "Fixed include x: 1 -> 2 (ci.yml:1)"
        ]
        # probe + final
        assert mock_runner.run.call_count == 2

    def test_fix_policies_rejects_dry_run(self):
        with pytest.raises(
            ValueError, match="--fix-policies cannot be used with --dry-run"
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_policies=True,
                dry_run=True,
            )

    def test_fix_policies_requires_token(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="--fix-policies requires a GitLab token"):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_policies=True,
                token="",
            )

    def test_create_mr_requires_a_fix_mode(self):
        with pytest.raises(
            ValueError,
            match="--create-mr requires --fix and/or --fix-policies",
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                create_mr=True,
                fix_supply_chain=False,
                fix_policies=False,
            )
