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
{examples}
## CLI Help

```text
{help}
```
"""

COMMAND_EXAMPLES = {
    "check": [
        "gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml",
        (
            "gitlab-compliance check -f oci://registry.example.com/org/"
            "gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml --update"
        ),
        (
            "gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml "
            "--format markdown -o COMPLIANCE-REPORT.md"
        ),
    ],
    "generate": [
        (
            "gitlab-compliance generate -i .gitlab-ci.yml --format "
            "swagger-markdown -o pipeline-reference.md"
        ),
        (
            "gitlab-compliance generate -i .gitlab-ci.yml --format "
            "swagger-markdown --exclude variables,image --group-by stage"
        ),
        (
            "gitlab-compliance generate -i .gitlab-ci.yml --format html "
            "-o pipeline-reference.html"
        ),
    ],
    "generate-html": [
        (
            "gitlab-compliance generate -i .gitlab-ci.yml --format html "
            "-o gitlab-compliance.html"
        ),
    ],
    "get-attributes": [
        (
            "gitlab-compliance get-attributes -i .gitlab-ci.yml "
            "-a stage,image,rules -o attributes.md"
        ),
        "gitlab-compliance get-attributes -i .gitlab-ci.yml -a image -j true",
    ],
    "policies": [
        "gitlab-compliance policies doc -f policies/security/ -o policy-catalog.md",
        (
            "gitlab-compliance policies push -f policies/security/ "
            "registry.example.com/org/gitlab-ci-policies:1.0.0"
        ),
        (
            "gitlab-compliance policies pull "
            "registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/security/"
        ),
    ],
    "policies doc": [
        "gitlab-compliance policies doc -f policies/security/ -o policy-catalog.md",
        (
            "gitlab-compliance policies doc -f policies/security/ --format html "
            "-o policy-catalog.html"
        ),
    ],
    "policies push": [
        (
            "gitlab-compliance policies push -f policies/security/ "
            "registry.example.com/org/gitlab-ci-policies:1.0.0"
        ),
    ],
    "policies pull": [
        (
            "gitlab-compliance policies pull "
            "registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/security/"
        ),
    ],
    "release-notes": [
        (
            "gitlab-compliance release-notes --projects my-group/my-project "
            "--markdown release-notes"
        ),
        (
            "gitlab-compliance release-notes --projects 12345 --since-tag v1.2.0 "
            "--no-write"
        ),
    ],
}


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


def _type_label(param_type) -> str:
    rendered = str(param_type)
    if not rendered.startswith("<click.types."):
        return rendered
    name = getattr(param_type, "name", None)
    if name:
        return str(name).upper()
    return param_type.__class__.__name__.replace("ParamType", "").upper()


def _param_metadata(param):
    if isinstance(param, click.Argument):
        return {
            "usage": param.name,
            "required": param.required,
            "default": param.default,
            "help": getattr(param, "help", None),
            "type": _type_label(param.type),
            "kind": "argument",
        }
    return {
        "usage": ", ".join(param.opts),
        "prompt": getattr(param, "prompt", None),
        "required": param.required,
        "default": param.default,
        "help": getattr(param, "help", None),
        "type": _type_label(param.type),
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


def _format_examples(command_name: str) -> str:
    examples = COMMAND_EXAMPLES.get(command_name, [])
    if not examples:
        return ""
    body = "\n".join(f"{example}" for example in examples)
    return f"## Examples\n\n```bash\n{body}\n```\n\n"


def _render_command_page(helpdct: dict, title: str | None = None) -> str:
    command = helpdct["command"]
    options = {opt.name: _param_metadata(opt) for opt in helpdct.get("params", [])}
    description = (command.help or "").strip()
    heading = title or command.name
    body = md_base_template.format(
        usage=helpdct.get("usage"),
        options=_format_options(options),
        examples=_format_examples(heading),
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
        "# Command Reference\n",
        f"Auto-generated reference for `{root_name}` subcommands.\n",
        "\n",
        "| Workflow | Commands |\n",
        "| -------- | -------- |\n",
        (
            "| Compliance checks | [`check`](check.md), "
            "[`policies`](policies.md), [`policies doc`](policies-doc.md) |\n"
        ),
        (
            "| Policy distribution | [`policies push`](policies-push.md), "
            "[`policies pull`](policies-pull.md) |\n"
        ),
        (
            "| Pipeline documentation | [`generate`](generate.md), "
            "[`get-attributes`](get-attributes.md) |\n"
        ),
        (
            "| Release support | [`release-notes`](release-notes.md) |\n"
        ),
        (
            "| Legacy and maintenance | [`generate-html`](generate-html.md), "
            "[`dumps`](dumps.md) |\n"
        ),
        "\n",
        "## All commands\n",
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
