import importlib
import pathlib
import re

import click

md_base_template = """
### Usage

```
{usage}
```

### Options
{options}

### CLI Help

```
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


def _render_command_page(helpdct: dict) -> str:
    command = helpdct["command"]
    options = {opt.name: _param_metadata(opt) for opt in helpdct.get("params", [])}
    description = (command.help or "").strip()
    body = md_base_template.format(
        usage=helpdct.get("usage"),
        options=_format_options(options),
        help=helpdct.get("help"),
    )
    if description:
        return f"# {command.name}\n\n{description}\n{body}"
    return f"# {command.name}\n{body}"


def _command_filename(command_name: str) -> str:
    safe_name = re.sub(r"[^\w.-]+", "-", command_name).strip("-").lower()
    return f"{safe_name}.md"


def dump_helper(base_command, docs_dir) -> list[str]:
    """Write one markdown file per top-level subcommand."""
    docs_path = pathlib.Path(docs_dir)
    docs_path.mkdir(parents=True, exist_ok=True)

    root_name = base_command.name
    written: list[str] = []

    for helpdct in recursive_help(base_command):
        command = helpdct["command"]
        parent = helpdct.get("parent", "") or ""

        if command is base_command or parent != root_name:
            continue

        filename = _command_filename(command.name)
        (docs_path / filename).write_text(
            _render_command_page(helpdct),
            encoding="utf-8",
        )
        written.append(command.name)

    index_lines = [
        "# Command Reference\n",
        f"Auto-generated reference for `{root_name}` subcommands.\n",
    ]
    for name in sorted(written):
        index_lines.append(f"- [{name}]({_command_filename(name)})\n")
    (docs_path / "command-reference.md").write_text("".join(index_lines), encoding="utf-8")

    return written


@click.group()
def cli():
    pass


@cli.command("dumps", hidden=True)
@click.option(
    "--baseModule",
    "base_module",
    help="The base command module path to import",
    required=True,
    default="src.gitlab_docs",
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
    Create one markdown file per top-level subcommand under --docsPath.
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


cli.add_command(cli)
