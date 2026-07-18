import importlib
import pathlib
import re

import click

MANUAL_DOCS_START = "<!-- MANUAL DOCS:START -->"
MANUAL_DOCS_END = "<!-- MANUAL DOCS:END -->"

md_base_template = """
## Usage

```
{usage}
```

## Options
{options}

## CLI Help

```
{help}
```
"""


def _extract_manual_docs(text: str) -> str | None:
    """Return the MANUAL DOCS block (markers included), or None if absent.

    Markers must appear alone on a line so CLI help that *mentions* the
    comments is not treated as a manual block.
    """
    pattern = re.compile(
        rf"^{re.escape(MANUAL_DOCS_START)}\s*\n.*?^{re.escape(MANUAL_DOCS_END)}\s*$",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(0) if match else None


def _with_manual_docs(rendered: str, existing: str | None) -> str:
    """Preserve a MANUAL DOCS block, inserting it before ``## Usage`` when present.

    That keeps demos/narrative above the generated options dump.
    """
    if not existing:
        return rendered
    manual = _extract_manual_docs(existing)
    if not manual:
        return rendered
    usage_marker = "\n## Usage\n"
    if usage_marker in rendered:
        before, after = rendered.split(usage_marker, 1)
        return before.rstrip() + "\n\n" + manual + "\n" + usage_marker + after
    return rendered.rstrip() + "\n\n" + manual + "\n"


def recursive_help(cmd, parent=None):
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)

    yield {
        "command": cmd,
        "help": cmd.get_help(ctx),
        "parent": parent.info_name if parent else "",
        "usage": cmd.get_usage(ctx),
        "params": cmd.get_params(ctx),
        "options": cmd.collect_usage_pieces(ctx),
    }

    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        for helpdct in recursive_help(sub, ctx):
            yield helpdct


def _param_metadata(param):
    if isinstance(param, click.Argument):
        return {
            "usage": param.name,
            "required": param.required,
            "default": param.default,
            "help": getattr(param, "help", None),
            "type": str(param.type),
            "kind": "argument",
        }
    return {
        "usage": "\n".join(param.opts),
        "prompt": getattr(param, "prompt", None),
        "required": param.required,
        "default": param.default,
        "help": getattr(param, "help", None),
        "type": str(param.type),
        "kind": "option",
    }


def _format_options(options: dict) -> str:
    if not options:
        return "_No options._\n"
    return "\n".join(
        [
            f"* `{opt_name}`{' (REQUIRED)' if opt.get('required') else ''}"
            f"{' [argument]' if opt.get('kind') == 'argument' else ''}: \n"
            f"  * Type: {opt.get('type')} \n"
            f"  * Default: `{str(opt.get('default')).lower()}`\n"
            f"  * Usage: `{opt.get('usage')}`\n"
            "\n"
            f"  {opt.get('help') or ''}\n"
            for opt_name, opt in options.items()
        ]
    )


def _render_command_page(helpdct: dict, title: str | None = None) -> str:
    command = helpdct["command"]
    options = {opt.name: _param_metadata(opt) for opt in helpdct.get("params", [])}
    description = (command.help or "").strip()
    heading = title or command.name
    body = md_base_template.format(
        usage=helpdct.get("usage"),
        options=_format_options(options),
        help=helpdct.get("help"),
    )
    if description:
        return f"# {heading}\n\n{description}\n{body}"
    return f"# {heading}\n{body}"


def _command_doc_slug(path: tuple[str, ...]) -> str:
    safe_parts = [
        re.sub(r"[^\w.-]+", "-", segment).strip("-").lower() for segment in path
    ]
    return "-".join(part for part in safe_parts if part)


def _command_doc_filename(path: tuple[str, ...]) -> str:
    return f"{_command_doc_slug(path)}.md"


def _iter_command_docs(base_command):
    def walk(cmd, parent_ctx, path: tuple[str, ...]):
        ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent_ctx)
        helpdct = {
            "command": cmd,
            "help": cmd.get_help(ctx),
            "parent": parent_ctx.info_name if parent_ctx else "",
            "usage": cmd.get_usage(ctx),
            "params": cmd.get_params(ctx),
            "options": cmd.collect_usage_pieces(ctx),
        }

        if cmd is not base_command:
            full_path = path + (cmd.name,)
            yield helpdct, full_path

        if isinstance(cmd, click.Group):
            child_path = path + (cmd.name,) if cmd is not base_command else path
            for sub in cmd.commands.values():
                yield from walk(sub, ctx, child_path)

    yield from walk(base_command, None, ())


def dump_helper(base_command, docs_dir) -> list[str]:
    """Write one markdown file per CLI subcommand (including nested groups)."""
    docs_path = pathlib.Path(docs_dir)
    docs_path.mkdir(parents=True, exist_ok=True)

    root_name = base_command.name
    written: list[tuple[str, ...]] = []

    for helpdct, command_path in _iter_command_docs(base_command):
        display_name = " ".join(command_path)
        filename = _command_doc_filename(command_path)
        target = docs_path / filename
        existing = target.read_text(encoding="utf-8") if target.is_file() else None
        target.write_text(
            _with_manual_docs(
                _render_command_page(helpdct, title=display_name),
                existing,
            ),
            encoding="utf-8",
        )
        written.append(command_path)

    index_lines = [
        "# CLI subcommands\n",
        f"Auto-generated index of `{root_name}` subcommands (see Usage in docs).\n",
    ]
    for command_path in sorted(written, key=_command_doc_slug):
        display_name = " ".join(command_path)
        index_lines.append(
            f"- [{display_name}]({_command_doc_filename(command_path)})\n"
        )
    (docs_path / "command-reference.md").write_text(
        "".join(index_lines), encoding="utf-8"
    )

    return [" ".join(path) for path in written]


@click.group()
def cli():
    pass


@cli.command("dumps", hidden=True)
@click.option(
    "--baseModule",
    "base_module",
    help="The base command module path to import",
    required=True,
    default="src.gitlab_compliance",
)
@click.option(
    "--baseCommand",
    "base_command",
    help="The base command function to import",
    required=True,
    default="gitlab_compliance",
)
@click.option(
    "--docsPath",
    "docs_path",
    help="The docs dir path to write the md files",
    required=True,
    default="docs/usage/reference/",
)
def dumps(base_module, base_command, docs_path):
    """
    Create one markdown file per subcommand under --docsPath.

    Existing pages may keep a narrative block between MANUAL DOCS START/END
    HTML comments on their own lines; that block is preserved across
    regenerations.
    """
    click.secho(
        f"Creating command docs from {base_module}.{base_command} into {docs_path}",
        color="green",
    )

    try:
        module_ = importlib.import_module(base_module)
    except Exception as e:
        click.echo(f"Could not find module: {base_module}. Error: {str(e)}")
        return

    try:
        command_ = getattr(module_, base_command)
    except AttributeError:
        click.echo(f"Could not find command {base_command} on module {base_module}")
        return

    try:
        written = dump_helper(command_, docs_dir=docs_path)
        click.secho(
            f"Created {len(written)} command docs under {docs_path}",
            color="green",
        )
    except Exception as e:
        click.secho(f"Dumps command failed: {str(e)}", color="red")
        raise
