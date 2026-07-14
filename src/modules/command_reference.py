import importlib
import pathlib
import re

import click

md_base_template = """
## Usage

```text
{usage}
```

## Options

{options}
## CLI Help

```text
{help}
```
"""


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
    param_type = _format_param_type(param)
    if isinstance(param, click.Argument):
        return {
            "usage": param.name,
            "required": param.required,
            "default": param.default,
            "help": getattr(param, "help", None),
            "type": param_type,
            "kind": "argument",
        }
    option_flags = list(param.opts) + list(getattr(param, "secondary_opts", []))
    return {
        "usage": ", ".join(option_flags),
        "prompt": getattr(param, "prompt", None),
        "required": param.required,
        "default": param.default,
        "help": getattr(param, "help", None),
        "type": param_type,
        "kind": "option",
    }


def _format_param_type(param) -> str:
    """Return stable, human-friendly Click parameter type text."""
    param_type = param.type
    if isinstance(param_type, click.Choice):
        return "choice: " + ", ".join(f"`{choice}`" for choice in param_type.choices)
    type_name = getattr(param_type, "name", None)
    if type_name:
        return str(type_name)
    return str(param_type)


def _format_default(value) -> str:
    if value is None:
        return "`none`"
    if value is click.core.ParameterSource.DEFAULT:  # pragma: no cover - safety
        return "`default`"
    if value is Ellipsis:
        return "`...`"
    value_text = str(value)
    if value_text == "Sentinel.UNSET":
        return "_not set_"
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    return f"`{value_text}`"


def _escape_table_cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _format_options(options: dict) -> str:
    if not options:
        return "_No options._\n"
    rows = [
        "| Name | Type | Required | Default | Usage | Description |",
        "| ---- | ---- | -------- | ------- | ----- | ----------- |",
    ]
    for opt_name, opt in options.items():
        name = f"`{opt_name}`"
        if opt.get("kind") == "argument":
            name = f"{name} _(argument)_"
        rows.append(
            " | ".join(
                [
                    f"| {name}",
                    _escape_table_cell(opt.get("type", "")),
                    "yes" if opt.get("required") else "no",
                    _format_default(opt.get("default")),
                    f"`{_escape_table_cell(opt.get('usage', ''))}`",
                    _escape_table_cell(opt.get("help") or ""),
                ]
            )
            + " |"
        )
    return "\n".join(rows) + "\n"


def _command_description(command: click.Command) -> str:
    description = (command.help or "").strip()
    return re.sub(
        r"```([A-Za-z0-9_-]+)",
        r"`\1",
        description,
    )


def _render_command_page(helpdct: dict, title: str | None = None) -> str:
    command = helpdct["command"]
    options = {opt.name: _param_metadata(opt) for opt in helpdct.get("params", [])}
    description = _command_description(command)
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
        (docs_path / filename).write_text(
            _render_command_page(helpdct, title=display_name),
            encoding="utf-8",
        )
        written.append(command_path)

    index_lines = [
        "# Command Reference\n\n",
        f"Auto-generated reference for `{root_name}` subcommands.\n\n",
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
