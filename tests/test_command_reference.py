import click
from click.testing import CliRunner

from src.gitlab_compliance import gitlab_compliance
from src.modules.command_reference import (
    MANUAL_DOCS_END,
    MANUAL_DOCS_START,
    _extract_manual_docs,
    _format_options,
    _render_command_page,
    _with_manual_docs,
    dump_helper,
    dumps,
    recursive_help,
)


class TestRecursiveHelp:
    def test_yields_subcommands(self):
        entries = list(recursive_help(gitlab_compliance))
        names = {entry["command"].name for entry in entries}
        assert "generate" in names
        assert "check" in names
        assert "policies" in names


class TestDumpHelper:
    def test_writes_one_file_per_top_level_command(self, tmp_path):
        written = dump_helper(gitlab_compliance, tmp_path)
        assert "generate" in written
        assert "check" in written
        assert "policies doc" in written
        assert "document gitstrings" in written
        assert (tmp_path / "check.md").is_file()
        assert (tmp_path / "policies-doc.md").is_file()
        assert (tmp_path / "document-gitstrings.md").is_file()

        generate_md = tmp_path / "generate.md"
        assert generate_md.is_file()
        text = generate_md.read_text(encoding="utf-8")
        assert text.startswith("# generate")
        assert "## Usage" in text

        index_md = tmp_path / "command-reference.md"
        assert index_md.is_file()
        assert "[generate](generate.md)" in index_md.read_text(encoding="utf-8")

    def test_preserves_manual_docs_block(self, tmp_path):
        check_path = tmp_path / "check.md"
        check_path.write_text(
            "# check\n\nold generated body\n\n"
            f"{MANUAL_DOCS_START}\n\n## Keep me\n\n{MANUAL_DOCS_END}\n",
            encoding="utf-8",
        )
        dump_helper(gitlab_compliance, tmp_path)
        text = check_path.read_text(encoding="utf-8")
        assert MANUAL_DOCS_START in text
        assert "## Keep me" in text
        assert MANUAL_DOCS_END in text
        assert text.startswith("# check")
        assert "## Usage" in text
        assert text.index(MANUAL_DOCS_START) < text.index("## Usage")
        assert text.index(MANUAL_DOCS_END) < text.index("## Usage")


class TestManualDocsHelpers:
    def test_extract_and_merge(self):
        existing = f"generated\n\n{MANUAL_DOCS_START}\nnote\n{MANUAL_DOCS_END}\n"
        block = _extract_manual_docs(existing)
        assert block is not None
        assert "note" in block
        merged = _with_manual_docs("# title\n\nDesc\n\n## Usage\n\nbody\n", existing)
        assert merged.startswith("# title")
        assert MANUAL_DOCS_START in merged
        assert merged.index(MANUAL_DOCS_START) < merged.index("## Usage")
        assert _with_manual_docs("# new\n", None) == "# new\n"
        assert _with_manual_docs("# new\n", "no markers") == "# new\n"

    def test_ignores_markers_mentioned_inline(self):
        help_text = (
            "mentions ``<!-- MANUAL DOCS:START -->`` and "
            "``<!-- MANUAL DOCS:END -->`` inline\n"
        )
        assert _extract_manual_docs(help_text) is None


class TestDumpsCli:
    def test_writes_command_reference_markdown(self, tmp_path):
        docs_dir = tmp_path / "docs"
        runner = CliRunner()
        result = runner.invoke(
            dumps,
            [
                "--baseModule",
                "src.gitlab_compliance",
                "--baseCommand",
                "gitlab_compliance",
                "--docsPath",
                str(docs_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert (docs_dir / "generate.md").is_file()
        assert (docs_dir / "check.md").is_file()
        assert (docs_dir / "policies-doc.md").is_file()
        assert (docs_dir / "document-gitstrings.md").is_file()
        assert (docs_dir / "shell-check.md").is_file()
        assert (docs_dir / "supply-chain.md").is_file()
        index_text = (docs_dir / "command-reference.md").read_text(encoding="utf-8")
        assert "# CLI subcommands" in index_text
        assert "Created 14 command docs" in result.output

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


class TestCommandReferenceHelpers:
    def test_format_options_empty(self):
        assert _format_options({}) == "_No options._\n"

    def test_render_command_page_without_description(self):
        @click.command()
        def bare_command():
            pass

        bare_command.help = None
        helpdct = {
            "command": bare_command,
            "usage": "Usage: bare-command",
            "params": [],
            "help": "Help text",
        }
        rendered = _render_command_page(helpdct, title="bare command")
        assert rendered.startswith("# bare command\n")
        assert "Help text" in rendered
