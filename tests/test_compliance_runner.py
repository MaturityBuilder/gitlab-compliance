import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.compliance.builtin_policies import BUILTIN_POLICIES_DIR
from src.compliance.runner import (
    _assert_within_directory,
    _collect_feature_files,
    _resolve_policy_directories,
    run_compliance,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PIPELINE = REPO_ROOT / "examples/sample-files" / ".gitlab-ci.yml"
PASSING_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "passing"
INCLUDE_VERSION_PASSING = (
    REPO_ROOT / "tests" / "compliance_policies" / "include-versions" / "passing.feature"
)
INCLUDE_VERSION_POLICIES = (
    REPO_ROOT / "tests" / "compliance_policies" / "include-versions"
)
INCLUDE_VERSION_PIPELINE = (
    REPO_ROOT / "examples/sample-files" / "gitlab-ci" / "includes_with_keys.yml"
)
OUTLINE_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "outlines"


class TestFeatureFileGuards:
    def test_rejects_path_outside_policies_root(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        outside = tmp_path / "evil.feature"
        outside.write_text("Feature: x\n", encoding="utf-8")
        with pytest.raises(ValueError, match="escapes policies directory"):
            _assert_within_directory(str(policies), str(outside))

    def test_invalid_commonpath_raises(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        feature = policies / "ok.feature"
        feature.write_text("Feature: ok\n", encoding="utf-8")

        with patch(
            "src.compliance.runner.os.path.commonpath",
            side_effect=ValueError("bad path"),
        ):
            with pytest.raises(ValueError, match="Invalid feature file path"):
                _assert_within_directory(str(policies), str(feature))

    def test_collect_feature_files_finds_nested(self, tmp_path):
        nested = tmp_path / "security"
        nested.mkdir()
        (nested / "rule.feature").write_text("Feature: R\n", encoding="utf-8")
        (tmp_path / "top.feature").write_text("Feature: T\n", encoding="utf-8")
        found = _collect_feature_files(str(tmp_path))
        assert len(found) == 2


class TestRunCompliance:
    def test_missing_pipeline_raises(self):
        with pytest.raises(FileNotFoundError, match="Pipeline file not found"):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file="/no/such/pipeline.yml",
            )

    def test_empty_policies_dir_raises(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(FileNotFoundError, match="No .feature files"):
            run_compliance(
                features_dir=str(empty),
                pipeline_file=str(SAMPLE_PIPELINE),
            )

    def test_passing_run_returns_success(self):
        result = run_compliance(
            features_dir=str(PASSING_POLICIES),
            pipeline_file=str(SAMPLE_PIPELINE),
            output_format="markdown",
        )
        assert result.success is True
        assert result.exit_code == 0
        assert result.passed >= 1


class TestIncludeVersionPolicies:
    def test_semver_include_policy_passes(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            INCLUDE_VERSION_PASSING.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(INCLUDE_VERSION_PIPELINE),
        )
        assert result.success is True

    def test_branch_ref_include_policy_fails(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "failing.feature").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(SAMPLE_PIPELINE),
        )
        assert result.success is False
        assert result.failed >= 1

    def test_latest_release_policy_skips_without_api_token(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-latest.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(INCLUDE_VERSION_PIPELINE),
        )
        assert result.success is True
        assert result.skipped >= 1

    def test_latest_release_policy_fails_when_update_available(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-latest.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "9.9.9"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is False
        assert result.failed >= 1

    def test_grace_days_policy_passes_within_window(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-grace-days.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "9.9.9"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["latest_release_age_days"] = 10
                item["release_lag_days"] = 200
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is True

    def test_grace_days_policy_fails_beyond_window(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-grace-days.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "9.9.9"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["latest_release_age_days"] = 45
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is False
        assert result.failed >= 1

    def test_lag_days_policy_passes_within_threshold(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-lag-days.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "9.9.9"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["release_lag_days"] = 30
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is True

    def test_lag_days_policy_fails_beyond_threshold(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-lag-days.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "9.9.9"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["release_lag_days"] = 120
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is False
        assert result.failed >= 1

    def test_latest_tags_policy_passes_within_window(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-latest-tags.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "2.0.0"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["version_tag_rank"] = 2
                item["semver_tag_count"] = 5
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is True

    def test_latest_tags_policy_fails_outside_window(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            (INCLUDE_VERSION_POLICIES / "api-latest-tags.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )

        def _fake_enrich(includes, *, gitlab_url, token, **kwargs):
            enriched = []
            for include in includes:
                item = dict(include)
                item["valid_version"] = True
                item["latest_version"] = "3.0.0"
                item["update_available"] = True
                item["release_metadata_resolved"] = True
                item["version_tag_rank"] = 5
                item["semver_tag_count"] = 8
                enriched.append(item)
            return enriched

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=_fake_enrich,
        ):
            result = run_compliance(
                features_dir=str(policies),
                pipeline_file=str(INCLUDE_VERSION_PIPELINE),
                token="secret",
            )

        assert result.success is False
        assert result.failed >= 1


COMPONENT_PINNING_FEATURE = (
    REPO_ROOT / "examples/example-policies" / "security" / "component-pinning.feature"
)


class TestComponentPinningPolicies:
    def test_skips_when_pipeline_has_no_component_includes(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("component.feature").write_text(
            COMPONENT_PINNING_FEATURE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n"
            "  - project: org/templates\n"
            "    ref: 1.0.0\n"
            "    file: ci.yml\n"
            "job:\n"
            "  script:\n"
            "    - echo hi\n",
            encoding="utf-8",
        )

        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
            output_format="markdown",
        )

        assert result.skipped == 3
        assert result.failed == 0
        assert all(s.status == "skipped" for s in result.scenario_results)

    def test_passes_when_component_uses_semver(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("component.feature").write_text(
            "Feature: Component semver\n"
            "  Scenario: Component includes must use semver\n"
            '    Given I have include type "component" defined\n'
            '    Then its version must match "^\\d+\\.\\d+\\.\\d+(-[\\w.]+)?$"\n',
            encoding="utf-8",
        )
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n"
            "  - component: gitlab.com/org/pipeline@1.2.0\n"
            "job:\n"
            "  script:\n"
            "    - echo hi\n",
            encoding="utf-8",
        )

        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
            output_format="markdown",
        )

        assert result.success is True
        assert result.passed == 1

    def test_fails_when_component_tracks_branch(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("component.feature").write_text(
            "Feature: Component branch\n"
            "  Scenario: Component includes must not track a branch\n"
            '    Given I have include type "component" defined\n'
            '    Then its version must not match "^(main|master|develop)$"\n',
            encoding="utf-8",
        )
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n"
            "  - component: gitlab.com/org/pipeline@main\n"
            "job:\n"
            "  script:\n"
            "    - echo hi\n",
            encoding="utf-8",
        )

        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
            output_format="markdown",
        )

        assert result.success is False
        assert result.failed == 1


class TestRunComplianceFix:
    def test_fix_with_dry_run_raises(self):
        with pytest.raises(
            ValueError, match="--fix-supply-chain cannot be used with --dry-run"
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                dry_run=True,
            )

    def test_fix_without_token_raises(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        with pytest.raises(
            ValueError, match="--fix-supply-chain requires a GitLab token"
        ):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
            )

    def test_fix_invokes_supply_chain_fixes(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "secret")
        with (
            patch(
                "src.compliance.supply_chain_fix.apply_supply_chain_fixes",
                return_value=[
                    "Fixed include platform/ci-templates: 1.0.0 -> 2.0.0 (ci.yml:2)"
                ],
            ) as apply_fixes,
            patch("src.compliance.runner.Runner") as mock_runner_cls,
        ):
            mock_runner_cls.return_value.run.return_value = 0
            mock_runner_cls.return_value.features = []
            result = run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                token="secret",
                output_format="markdown",
            )

        assert result.success is True
        apply_fixes.assert_called_once_with(
            pipeline_file=str(SAMPLE_PIPELINE),
            include_nested=True,
            max_include_depth=None,
            gitlab_url=None,
            token="secret",
            project=None,
            group=None,
        )


class TestResolvePolicyDirectories:
    def test_with_builtin_includes_package_dir(self):
        dirs = _resolve_policy_directories(str(PASSING_POLICIES), with_builtin=True)
        assert os.path.abspath(BUILTIN_POLICIES_DIR) in dirs
        assert os.path.abspath(str(PASSING_POLICIES)) in dirs

    def test_without_builtin_only_user_dir(self):
        dirs = _resolve_policy_directories(str(PASSING_POLICIES), with_builtin=False)
        assert len(dirs) == 1
        assert dirs[0] == os.path.abspath(str(PASSING_POLICIES))


class TestScenarioOutlinePolicies:
    def test_variable_outline_expands_and_passes(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("outline.feature").write_text(
            (OUTLINE_POLICIES / "variable-outline.feature").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(SAMPLE_PIPELINE),
        )
        assert result.success is True
        assert result.passed >= 1
        assert any(
            "Pipeline variables must match" in r.name for r in result.scenario_results
        )

    def test_variable_outline_failing_row(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("fail.feature").write_text(
            (OUTLINE_POLICIES / "variable-outline-failing.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(SAMPLE_PIPELINE),
        )
        assert result.success is False
        assert result.failed >= 1

    def test_component_input_outline_passes(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("component.feature").write_text(
            (OUTLINE_POLICIES / "component-input-outline.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(OUTLINE_POLICIES / "component-input-pipeline.yml"),
        )
        assert result.success is True
        assert result.passed >= 2

    def test_component_input_outline_fails(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("component.feature").write_text(
            (OUTLINE_POLICIES / "component-input-outline.feature").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(
                OUTLINE_POLICIES / "component-input-failing-pipeline.yml"
            ),
        )
        assert result.success is False
        assert result.failed >= 1

    def test_variable_outline_regex_row_passes(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("allowlist.feature").write_text(
            (
                REPO_ROOT / "src/compliance/builtin_policies/variable-allowlist.feature"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "variables:\n"
            "  APPLICATION: my-app\n"
            "  ENVIRONMENT: prod\n"
            "  ROLE: backend\n"
            "job:\n"
            "  script:\n"
            "    - echo hi\n",
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
        )
        assert result.success is True
        assert result.passed >= 3
        assert result.failed == 0

    def test_variable_outline_skips_when_key_absent(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("outline.feature").write_text(
            (OUTLINE_POLICIES / "variable-outline.feature").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "variables:\n" "  OTHER: value\n" "job:\n" "  script:\n" "    - echo hi\n",
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
        )
        assert result.skipped >= 1
        assert result.failed == 0
        assert all(s.status != "failed" for s in result.scenario_results)

    def test_outline_metadata_attached(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("metadata.feature").write_text(
            (OUTLINE_POLICIES / "metadata-outline.feature").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(SAMPLE_PIPELINE),
        )
        assert result.success is True
        assert any(
            s.policy_id == "GLCI-OUTLINE-TEST-001" for s in result.scenario_results
        )


class TestWithBuiltinPolicies:
    def test_with_builtin_merges_policies(self):
        result = run_compliance(
            features_dir=str(PASSING_POLICIES),
            pipeline_file=str(SAMPLE_PIPELINE),
            with_builtin=True,
        )
        assert result.scenarios >= 2
        policy_ids = {s.policy_id for s in result.scenario_results if s.policy_id}
        assert any(pid.startswith("GLCI-BUILTIN") for pid in policy_ids)
