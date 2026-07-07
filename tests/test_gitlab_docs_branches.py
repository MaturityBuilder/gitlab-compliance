import os
import shutil
from unittest.mock import patch

from click.testing import CliRunner

from src.compliance.models import ComplianceResult
from src.gitlab_compliance import check


class TestComplianceCacheUpdate:
    def test_update_clears_policy_cache_dir(self, tmp_path, monkeypatch):
        cache = tmp_path / "cache"
        cache.mkdir()
        (cache / "old.feature").write_text("Feature: X\n", encoding="utf-8")

        monkeypatch.setattr(
            "src.gitlab_docs.is_oci_reference",
            lambda _value: True,
        )
        monkeypatch.setattr(
            "src.gitlab_docs.run_compliance",
            lambda **kwargs: ComplianceResult(
                success=True,
                exit_code=0,
                scenario_results=[],
                scenarios=0,
                passed=0,
                failed=0,
                skipped=0,
            ),
        )

        runner = CliRunner()
        result = runner.invoke(
            check,
            [
                "--features",
                "oci://registry.example.com/policies:1.0.0",
                "--pipeline",
                os.fspath(
                    __import__("pathlib").Path(__file__).resolve().parents[1]
                    / "examples/sample-files"
                    / ".gitlab-ci.yml"
                ),
                "--update",
                "--policy-cache-dir",
                os.fspath(cache),
            ],
        )
        assert result.exit_code == 0, result.output
        assert not cache.exists() or not any(cache.iterdir())
