from click.testing import CliRunner

from src.gitlab_docs import gitlab_compliance
from src.modules.command_reference import dumps, recursive_help


class TestRecursiveHelp:
    def test_yields_subcommands(self):
        entries = list(recursive_help(gitlab_compliance))
        names = {entry["command"].name for entry in entries}
        assert "generate" in names
        assert "compliance" in names


class TestDumpsCli:
    def test_writes_command_reference_markdown(self, tmp_path):
        docs_dir = tmp_path / "docs"
        runner = CliRunner()
        result = runner.invoke(
            dumps,
            [
                "--baseModule",
                "src.gitlab_docs",
                "--baseCommand",
                "gitlab_compliance",
                "--docsPath",
                str(docs_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        md_path = docs_dir / "command-reference.md"
        assert md_path.is_file()
        text = md_path.read_text(encoding="utf-8")
        assert "# Command Reference" in text
        assert "generate" in text.lower()

    def test_missing_module_reports_error(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            dumps,
            [
                "--baseModule",
                "not_a_real_module_xyz",
                "--baseCommand",
                "gitlab_compliance",
                "--docsPath",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Could not find module" in result.output
