from click.testing import CliRunner

from src.gitlab_docs import gitlab_compliance
from src.modules.command_reference import dumps, dump_helper, recursive_help


class TestRecursiveHelp:
    def test_yields_subcommands(self):
        entries = list(recursive_help(gitlab_compliance))
        names = {entry["command"].name for entry in entries}
        assert "generate" in names
        assert "compliance" in names


class TestDumpHelper:
    def test_writes_one_file_per_top_level_command(self, tmp_path):
        written = dump_helper(gitlab_compliance, tmp_path)
        assert "generate" in written
        assert "compliance" in written
        assert "gitlab-compliance" not in written

        generate_md = tmp_path / "generate.md"
        assert generate_md.is_file()
        text = generate_md.read_text(encoding="utf-8")
        assert text.startswith("# generate")
        assert "### Usage" in text

        index_md = tmp_path / "command-reference.md"
        assert index_md.is_file()
        assert "[generate](generate.md)" in index_md.read_text(encoding="utf-8")


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
        assert (docs_dir / "generate.md").is_file()
        assert (docs_dir / "compliance.md").is_file()
        index_text = (docs_dir / "command-reference.md").read_text(encoding="utf-8")
        assert "# Command Reference" in index_text
        assert "Created 9 command docs" in result.output

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
