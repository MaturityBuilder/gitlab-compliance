import importlib
import os
import pathlib

import click

md_base_template = """
## {command_name}

{description}

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


def dump_helper(base_command, docs_dir):
    """Dumping help usage files from Click Help files into an md"""
    docs_path = pathlib.Path(docs_dir)
    for helpdct in recursive_help(base_command):
        command = helpdct.get("command")
        helptxt = helpdct.get("help")
        usage = helpdct.get("usage")
        parent = helpdct.get("parent", "") or ""
        options = {opt.name: _param_metadata(opt) for opt in helpdct.get("params", [])}
        full_command = (
            f"{str(parent) + ' ' if parent else ''}{str(command.name)}".replace(
                "gitlab-docs", ""
            )
        )

        if not full_command:
            full_command = f"{str(parent) + ' ' if parent else ''}{str(command.name)}"
        print(full_command)
        md_template = md_base_template.format(
            command_name=full_command,
            description=command.help,
            usage=usage,
            options="\n".join(
                [
                    f"* `{opt_name}`{' (REQUIRED)' if opt.get('required') else ''}{' [argument]' if opt.get('kind') == 'argument' else ''}: \n"
                    f"  * Type: {opt.get('type')} \n"
                    f"  * Default: `{str(opt.get('default')).lower()}`\n"
                    f"  * Usage: `{opt.get('usage')}`\n"
                    "\n"
                    f"  {opt.get('help') or ''}\n"
                    f"\n"
                    for opt_name, opt in options.items()
                ]
            ),
            help=helptxt,
        )

        if not docs_path.exists():
            docs_path.mkdir(parents=True, exist_ok=True)

        md_file_path = docs_path.joinpath("command-reference.md").absolute()
        # full_command.replace(' ', '-').lower() + '.md')

        # Create the file per each command
        with open(md_file_path, "a") as md_file:
            md_file.write(md_template)


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
    default="docs/",
)
def dumps(base_module, base_command, docs_path):
    """
    # Click-md
    Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.
    """
    md_file_path = os.path.join(docs_path, "command-reference.md")
    os.makedirs(docs_path, exist_ok=True)
    with open(md_file_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Command Reference")
    click.secho(
        f"Creating a new documents from {base_module}.{base_command} into {docs_path}",
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
        dump_helper(command_, docs_dir=docs_path)
        click.secho(f"Created docs under {docs_path}", color="green")
    except Exception as e:
        click.secho(f"Dumps command failed: {str(e)}", color="red")
        raise


cli.add_command(cli)
