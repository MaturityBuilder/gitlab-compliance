import json
from pathlib import Path

from click.testing import CliRunner

from src.gitlab_docs import compliance, compliance_doc, generate, get_attributes

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PIPELINE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"
PASSING_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "passing"
FAILING_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "failing"
ANNOTATED_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "annotated"


class TestGenerateCli:
    def test_dry_mode_skips_writing_output(self, tmp_path):
        output_file = tmp_path / "README.md"
        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                "--input-config",
                str(SAMPLE_PIPELINE),
                "--output-file",
                str(output_file),
                "--dry-mode",
            ],
        )
        assert result.exit_code == 0, result.output
        assert not output_file.exists()

    def test_markdown_generation_writes_output(self, tmp_path):
        output_file = tmp_path / "docs.md"
        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                "--input-config",
                str(SAMPLE_PIPELINE),
                "--output-file",
                str(output_file),
            ],
        )
        assert result.exit_code == 0, result.output
        content = output_file.read_text(encoding="utf-8")
        assert "gitlab-docs-opening-auto-generated" in content or len(content) > 0


class TestGetAttributesCli:
    def test_get_attributes_writes_markdown_table(self, tmp_path):
        output_file = tmp_path / "attrs.md"
        runner = CliRunner()
        result = runner.invoke(
            get_attributes,
            [
                "--input-config",
                str(SAMPLE_PIPELINE),
                "--output-file",
                str(output_file),
                "--attributes",
                "stage,image",
            ],
        )
        assert result.exit_code == 0, result.output
        assert output_file.exists()
        assert output_file.stat().st_size > 0


class TestComplianceCli:
    def test_passing_policies_exit_zero(self):
        runner = CliRunner()
        result = runner.invoke(
            compliance,
            [
                "--features",
                str(PASSING_POLICIES),
                "--pipeline",
                str(SAMPLE_PIPELINE),
            ],
        )
        assert result.exit_code == 0, result.output

    def test_failing_policies_exit_nonzero(self):
        runner = CliRunner()
        result = runner.invoke(
            compliance,
            [
                "--features",
                str(FAILING_POLICIES),
                "--pipeline",
                str(SAMPLE_PIPELINE),
            ],
        )
        assert result.exit_code != 0, result.output

    def test_codequality_report_written_to_file(self, tmp_path):
        report_path = tmp_path / "gl-code-quality-report.json"
        runner = CliRunner()
        result = runner.invoke(
            compliance,
            [
                "--features",
                str(FAILING_POLICIES),
                "--pipeline",
                str(SAMPLE_PIPELINE),
                "--format",
                "codequality",
                "--output-file",
                str(report_path),
            ],
        )
        assert result.exit_code != 0, result.output
        assert report_path.is_file()
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert isinstance(payload, list)
        assert payload, "expected at least one word finding"


class TestComplianceDocCli:
    def test_policy_catalog_markdown(self, tmp_path):
        output_path = tmp_path / "catalog.md"
        runner = CliRunner()
        result = runner.invoke(
            compliance_doc,
            [
                "--features",
                str(ANNOTATED_POLICIES),
                "--output-file",
                str(output_path),
            ],
        )
        assert result.exit_code == 0, result.output
        text = output_path.read_text(encoding="utf-8")
        assert "Policy" in text or "policy" in text.lower()
