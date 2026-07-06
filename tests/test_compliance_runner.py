from pathlib import Path

import pytest

from src.compliance.runner import (
    _assert_within_directory,
    _collect_feature_files,
    run_compliance,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PIPELINE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"
PASSING_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "passing"


class TestFeatureFileGuards:
    def test_rejects_path_outside_policies_root(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        outside = tmp_path / "evil.feature"
        outside.write_text("Feature: x\n", encoding="utf-8")
        with pytest.raises(ValueError, match="escapes policies directory"):
            _assert_within_directory(str(policies), str(outside))

    def test_invalid_commonpath_raises(self, tmp_path, monkeypatch):
        policies = tmp_path / "policies"
        policies.mkdir()
        feature = policies / "ok.feature"
        feature.write_text("Feature: ok\n", encoding="utf-8")

        def broken_commonpath(_a, _b):
            raise ValueError("bad path")

        monkeypatch.setattr("src.compliance.runner.os.path.commonpath", broken_commonpath)
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
