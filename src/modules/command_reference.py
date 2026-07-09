import importlib
import pathlib
import re

import click

from src.modules.doc_controller import update_marked_block

COMMAND_REFERENCE_MARKER_START = (
    "<!-- gitlab-compliance-command-reference-opening-auto-generated -->"
)
COMMAND_REFERENCE_MARKER_END = (
    "<!-- gitlab-compliance-command-reference-closing-auto-generated -->"
)

md_base_template = """
{demo}
{extra}

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

COMMAND_DEMO_GIFS = {
    ("check",): {
        "path": "../../assets/command-reference/check-demo.gif",
        "alt": "Animated terminal demo for gitlab-compliance check",
    },
    ("generate",): {
        "path": "../../assets/command-reference/generate-demo.gif",
        "alt": "Animated terminal demo for gitlab-compliance generate",
    },
    ("policies",): {
        "path": "../../assets/command-reference/policies-demo.gif",
        "alt": "Animated terminal demo for gitlab-compliance policies",
    },
}

COMMAND_EXTRA_BLOCKS = {
    ("generate",): """## Output examples

The `generate` command writes pipeline documentation in Markdown,
swagger-markdown, or HTML formats.

```bash
gitlab-compliance generate -i .gitlab-ci.yml --format markdown -o GITLAB-COMPLIANCE.md
gitlab-compliance generate -i .gitlab-ci.yml --format html -o public/index.html
```

### Markdown output

![Animated Markdown output preview](../../assets/command-reference/markdown-output-demo.gif)

```markdown
## GITLAB COMPLIANCE - .gitlab-ci.yml

## Inputs

| Key       | Value               | Description | Options   | Expand |
| --------- | ------------------- | ----------- | --------- | ------ |
| job-stage | {'default': 'test'} | _not set_   | _not set_ | true   |

## Variables

| Key         | Value          | Description | Options   | Expand |
| ----------- | -------------- | ----------- | --------- | ------ |
| APPLICATION | gitlab-docs    | _not set_   | _not set_ | true   |

## Jobs

### JOB - test

| Attribute | Value |
| --------- | ----- |
| stage     | test  |
```

### Swagger-style HTML output

![Animated Swagger-style HTML output preview](../../assets/command-reference/swagger-output-demo.gif)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitLab Docs - .gitlab-ci.yml</title>
</head>
<body>
  <header class="topbar">
    <h1>GitLab Docs</h1>
    <span class="config-file">.gitlab-ci.yml</span>
    <input class="search" id="search" type="search" placeholder="Filter jobs and sections">
  </header>
  <div class="layout">
    <nav class="sidebar">
      <a class="nav-link" href="#overview">Overview</a>
      <a class="nav-link" href="#jobs">Jobs<span class="nav-count">1</span></a>
    </nav>
    <main class="content">
      <section class="section" id="overview">
        <h2>Overview</h2>
        <p>Swagger-style documentation generated from <code>.gitlab-ci.yml</code>.</p>
      </section>
      <section class="section" id="jobs">
        <h2>Jobs</h2>
        <article class="opblock opblock-job" data-name="test" id="job-test">
          <button class="opblock-summary" type="button" aria-expanded="false">
            <span class="opblock-summary-method">JOB</span>
            <span class="opblock-summary-path">test</span>
          </button>
        </article>
      </section>
    </main>
  </div>
</body>
</html>
```
""",
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


def _normalise_text(value) -> str:
    return " ".join(str(value or "").split())


def _type_name(param_type) -> str:
    if isinstance(param_type, click.Choice):
        return "choice: " + ", ".join(param_type.choices)
    if isinstance(param_type, click.Path):
        return "path"
    return getattr(param_type, "name", str(param_type))


def _default_value(default) -> str:
    if default is None:
        return "None"
    default_text = str(default)
    if default_text == "sentinel.unset":
        return "None"
    return default_text


def _option_usage(param) -> str:
    if isinstance(param, click.Argument):
        return param.name
    return ", ".join([*param.opts, *param.secondary_opts])


def _escape_table(value) -> str:
    return str(value).replace("|", "\\|")


def _demo_gif_block(command_path: tuple[str, ...] | None) -> str:
    demo = COMMAND_DEMO_GIFS.get(command_path or ())
    if not demo:
        return ""
    return (
        "## Animated demo\n\n"
        f"![{demo['alt']}]({demo['path']})\n"
    )


def _extra_block(command_path: tuple[str, ...] | None) -> str:
    return COMMAND_EXTRA_BLOCKS.get(command_path or (), "")


def _format_options(options: dict) -> str:
    if not options:
        return "_No options._\n"

    rows = [
        "| Parameter | Required | Type | Default | Usage | Description |",
        "| --------- | -------- | ---- | ------- | ----- | ----------- |",
    ]
    for opt_name, opt in options.items():
        rows.append(
            "| `{name}` | {required} | `{type}` | `{default}` | `{usage}` | {help} |".format(
                name=_escape_table(opt_name),
                required="Yes" if opt.get("required") else "No",
                type=_escape_table(opt.get("type")),
                default=_escape_table(opt.get("default")),
                usage=_escape_table(opt.get("usage")),
                help=_escape_table(_normalise_text(opt.get("help")) or "-"),
            )
        )
    return "\n".join(rows) + "\n"


def _render_command_page(
    helpdct: dict,
    title: str | None = None,
    command_path: tuple[str, ...] | None = None,
) -> str:
    command = helpdct["command"]
    options = {}
    for opt in helpdct.get("params", []):
        metadata = _param_metadata(opt)
        metadata["usage"] = _option_usage(opt)
        metadata["type"] = _type_name(opt.type)
        metadata["default"] = _default_value(opt.default)
        options[opt.name] = metadata
    description = _normalise_text(command.help)
    heading = title or command.name
    body = md_base_template.format(
        demo=_demo_gif_block(command_path),
        extra=_extra_block(command_path),
        usage=(helpdct.get("usage") or "").strip(),
        options=_format_options(options),
        help=(helpdct.get("help") or "").strip(),
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


def _managed_markdown(content: str) -> str:
    return (
        f"{COMMAND_REFERENCE_MARKER_START}\n"
        f"{content.rstrip()}\n"
        f"{COMMAND_REFERENCE_MARKER_END}\n"
    )


def _write_managed_markdown(path: pathlib.Path, content: str) -> None:
    """Write generated command docs inside a replaceable marker block."""
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if (
            COMMAND_REFERENCE_MARKER_START in current
            and COMMAND_REFERENCE_MARKER_END in current
        ):
            update_marked_block(
                file_path=path,
                content=content,
                marker_start=COMMAND_REFERENCE_MARKER_START,
                marker_end=COMMAND_REFERENCE_MARKER_END,
            )
            return

    path.write_text(_managed_markdown(content), encoding="utf-8")


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
            if cmd.hidden:
                return
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
        _write_managed_markdown(
            docs_path / filename,
            _render_command_page(
                helpdct,
                title=display_name,
                command_path=command_path,
            ),
        )
        written.append(command_path)

    index_lines = [
        "# Command Reference\n\n",
        f"Auto-generated reference for `{root_name}` subcommands.\n\n",
        "![Animated terminal overview of gitlab-compliance commands](../../assets/command-reference/overview-demo.gif)\n\n",
    ]
    for command_path in sorted(written, key=_command_doc_slug):
        display_name = " ".join(command_path)
        index_lines.append(
            f"- [{display_name}]({_command_doc_filename(command_path)})\n"
        )
    _write_managed_markdown(docs_path / "command-reference.md", "".join(index_lines))

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
