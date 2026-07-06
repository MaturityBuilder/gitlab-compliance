from click.testing import CliRunner

from src import gitlab_docs as gitlab_docs_module
from src.gitlab_docs import gitlab_compliance, gitlab_docs


class TestDualCliEntryPoints:
    def test_gitlab_compliance_and_gitlab_docs_are_same_group(self):
        assert gitlab_compliance is gitlab_docs

    def test_gitlab_compliance_help_without_deprecation(self):
        runner = CliRunner()
        result = runner.invoke(gitlab_compliance, ["--help"], prog_name="gitlab-compliance")
        assert result.exit_code == 0
        assert "deprecated" not in result.output.lower()
        assert "compliance" in result.output.lower()

    def test_gitlab_docs_help_shows_deprecation_notice(self):
        runner = CliRunner()
        result = runner.invoke(gitlab_compliance, ["--help"], prog_name="gitlab-docs")
        assert result.exit_code == 0
        combined = f"{result.output}\n{getattr(result, 'stderr', '')}"
        assert "deprecated" in combined.lower()
        assert "gitlab-compliance" in combined

    def test_module_alias_points_at_shared_group(self):
        assert gitlab_docs_module.gitlab_docs is gitlab_compliance
