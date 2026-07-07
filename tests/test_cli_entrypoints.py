from click.testing import CliRunner

from src import gitlab_compliance as gitlab_compliance_module
from src.gitlab_compliance import gitlab_compliance


class TestDualCliEntryPoints:
    def test_gitlab_compliance_and_gitlab_compliance_are_same_group(self):
        assert gitlab_compliance is gitlab_compliance

    def test_gitlab_compliance_help_without_deprecation(self):
        runner = CliRunner()
        result = runner.invoke(
            gitlab_compliance, ["--help"], prog_name="gitlab-compliance"
        )
        assert result.exit_code == 0
        assert "deprecated" not in result.output.lower()
        assert "compliance" in result.output.lower()

    def test_gitlab_compliance_help_shows_deprecation_notice(self):
        runner = CliRunner()
        result = runner.invoke(
            gitlab_compliance, ["--help"], prog_name="gitlab-compliance"
        )
        assert result.exit_code == 0
        assert "deprecated" in result.output.lower()
        assert "gitlab-compliance" in result.output

    def test_module_alias_points_at_shared_group(self):
        assert gitlab_compliance_module.gitlab_compliance is gitlab_compliance
