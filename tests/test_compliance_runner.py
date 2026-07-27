import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.compliance.builtin_policies import (
    BUILTIN_POLICIES_DIR,
    BUILTIN_SHELL_POLICIES_DIR,
    BUILTIN_SUPPLY_CHAIN_POLICIES_DIR,
)
from src.compliance.metadata import iter_feature_files
from src.compliance.release_cache import ReleaseMetadataCache
from src.compliance.runner import (
    _assert_within_directory,
    _collect_feature_files,
    _resolve_policy_directories,
    resolve_policies_source_label,
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
        with pytest.raises(ValueError, match="--fix cannot be used with --dry-run"):
            run_compliance(
                features_dir=str(PASSING_POLICIES),
                pipeline_file=str(SAMPLE_PIPELINE),
                fix_supply_chain=True,
                dry_run=True,
            )

    def test_fix_without_token_raises(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="--fix requires a GitLab token"):
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
        apply_fixes.assert_called_once()
        kwargs = apply_fixes.call_args.kwargs
        assert kwargs["pipeline_file"] == str(SAMPLE_PIPELINE)
        assert kwargs["include_nested"] is True
        assert kwargs["max_include_depth"] is None
        assert kwargs["gitlab_url"] is None
        assert kwargs["token"] == "secret"
        assert kwargs["project"] is None
        assert kwargs["group"] is None
        assert isinstance(kwargs["cache"], ReleaseMetadataCache)


class TestResolvePolicyDirectories:
    def test_with_builtin_includes_package_dir(self):
        roots = _resolve_policy_directories(str(PASSING_POLICIES), with_builtin=True)
        paths = [root.path for root in roots]
        assert os.path.abspath(BUILTIN_POLICIES_DIR) in paths
        assert os.path.abspath(str(PASSING_POLICIES)) in paths
        builtin_root = next(
            root for root in roots if root.path == os.path.abspath(BUILTIN_POLICIES_DIR)
        )
        assert builtin_root.recursive is False

    def test_without_builtin_only_user_dir(self):
        roots = _resolve_policy_directories(str(PASSING_POLICIES), with_builtin=False)
        assert len(roots) == 1
        assert roots[0].path == os.path.abspath(str(PASSING_POLICIES))

    def test_without_features_dir_requires_builtin_or_shell_flag(self):
        with pytest.raises(ValueError, match="No policy source provided"):
            _resolve_policy_directories(None)

    def test_shell_check_only_without_features_dir(self):
        roots = _resolve_policy_directories(None, with_shell_check=True)
        assert [root.path for root in roots] == [
            os.path.abspath(BUILTIN_SHELL_POLICIES_DIR)
        ]

    def test_builtin_only_without_features_dir(self):
        roots = _resolve_policy_directories(None, with_builtin=True)
        assert len(roots) == 1
        assert roots[0].path == os.path.abspath(BUILTIN_POLICIES_DIR)
        assert roots[0].recursive is False

    def test_builtin_excludes_shell_and_supply_chain_subdirs(self):
        roots = _resolve_policy_directories(None, with_builtin=True)
        feature_files = list(
            iter_feature_files(roots[0].path, recursive=roots[0].recursive)
        )
        assert feature_files
        assert not any("/shell/" in path for path in feature_files)
        assert not any("/supply-chain/" in path for path in feature_files)

    def test_supply_chain_only_without_features_dir(self):
        roots = _resolve_policy_directories(None, with_supply_chain=True)
        assert [root.path for root in roots] == [
            os.path.abspath(BUILTIN_SUPPLY_CHAIN_POLICIES_DIR)
        ]

    def test_with_shell_check_includes_shell_policies_dir(self):
        roots = _resolve_policy_directories(
            str(PASSING_POLICIES), with_shell_check=True
        )
        paths = [root.path for root in roots]
        assert os.path.abspath(BUILTIN_SHELL_POLICIES_DIR) in paths
        assert os.path.abspath(str(PASSING_POLICIES)) in paths

    def test_with_builtin_and_shell_check_does_not_duplicate_shell_dir(self):
        roots = _resolve_policy_directories(
            str(PASSING_POLICIES),
            with_builtin=True,
            with_shell_check=True,
        )
        paths = [root.path for root in roots]
        assert paths.count(os.path.abspath(BUILTIN_SHELL_POLICIES_DIR)) == 1

    def test_resolve_policy_directories_dedupes_by_realpath(self, tmp_path):
        shell_link = tmp_path / "shell-link"
        shell_link.symlink_to(BUILTIN_SHELL_POLICIES_DIR)
        roots = _resolve_policy_directories(
            str(shell_link),
            with_shell_check=True,
        )
        paths = [root.path for root in roots]
        assert len(paths) == 1
        assert os.path.realpath(paths[0]) == os.path.realpath(
            BUILTIN_SHELL_POLICIES_DIR
        )

    def test_with_builtin_and_shell_check_does_not_duplicate_shell_scenarios(self):
        good_pipeline = (
            REPO_ROOT / "tests" / "fixtures" / "shell_check" / "good-pipeline.yml"
        )
        result = run_compliance(
            features_dir=None,
            pipeline_file=str(good_pipeline),
            with_builtin=True,
            with_shell_check=True,
        )
        shell_ids = [
            s.policy_id
            for s in result.scenario_results
            if s.policy_id.startswith("GLCI-SHELL")
        ]
        assert shell_ids
        assert len(shell_ids) == len(set(shell_ids))


class TestResolvePoliciesSourceLabel:
    def test_multiple_bundled_flags_join_labels(self):
        label = resolve_policies_source_label(
            None,
            with_builtin=True,
            with_shell_check=True,
            with_supply_chain=True,
        )
        assert BUILTIN_POLICIES_DIR in label
        assert BUILTIN_SHELL_POLICIES_DIR in label
        assert BUILTIN_SUPPLY_CHAIN_POLICIES_DIR in label
        assert ", " in label

    def test_features_dir_only_returns_user_dir(self):
        label = resolve_policies_source_label(str(PASSING_POLICIES))
        assert label == os.path.abspath(str(PASSING_POLICIES))

    def test_features_dir_plus_with_builtin_joins_labels(self):
        label = resolve_policies_source_label(
            str(PASSING_POLICIES),
            with_builtin=True,
        )
        assert os.path.abspath(str(PASSING_POLICIES)) in label
        assert BUILTIN_POLICIES_DIR in label
        assert ", " in label


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


class TestWithShellCheckPolicies:
    def test_with_shell_check_merges_shell_policies(self):
        good_pipeline = (
            REPO_ROOT / "tests" / "fixtures" / "shell_check" / "good-pipeline.yml"
        )
        result = run_compliance(
            features_dir=str(PASSING_POLICIES),
            pipeline_file=str(good_pipeline),
            with_shell_check=True,
        )
        policy_ids = {s.policy_id for s in result.scenario_results if s.policy_id}
        assert any(pid.startswith("GLCI-SHELL") for pid in policy_ids)
        assert any(pid == "GLCI-SHELL-PIN-003" for pid in policy_ids)
        assert not any(pid.startswith("GLCI-BUILTIN") for pid in policy_ids)

    def test_with_shell_check_only_without_features_dir(self):
        good_pipeline = (
            REPO_ROOT / "tests" / "fixtures" / "shell_check" / "good-pipeline.yml"
        )
        result = run_compliance(
            features_dir=None,
            pipeline_file=str(good_pipeline),
            with_shell_check=True,
        )
        policy_ids = {s.policy_id for s in result.scenario_results if s.policy_id}
        assert any(pid.startswith("GLCI-SHELL") for pid in policy_ids)
        assert result.success is True

    def test_without_policy_sources_raises(self):
        with pytest.raises(ValueError, match="No policy source provided"):
            run_compliance(
                features_dir=None,
                pipeline_file=str(SAMPLE_PIPELINE),
            )


class TestWithSupplyChainPolicies:
    def test_with_supply_chain_only_without_features_dir(self):
        result = run_compliance(
            features_dir=None,
            pipeline_file=str(SAMPLE_PIPELINE),
            with_supply_chain=True,
        )
        policy_ids = {s.policy_id for s in result.scenario_results if s.policy_id}
        assert any(pid.startswith("GLCI-IMAGE-PINNING") for pid in policy_ids)
        assert any(pid.startswith("GLCI-INCLUDE-VERSIONS") for pid in policy_ids)
