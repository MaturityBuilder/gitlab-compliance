"""
Gitlab-Docs entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

## Import Thirdparty Libraries
import os
import click
from datetime import datetime
import src.properties.includes as includes
import src.properties.jobs as jobs
import src.properties.variables as variables
import src.properties.inputs as inputs
import src.properties.workflows as workflows
from src.modules.logging import logger
import src.modules.doc_controller as md_writer
from src.modules.doc_controller import update_marked_block, add_between_markers


# ENABLE_WORKFLOW_DOCUMENTATION = os.getenv("ENABLE_WORKFLOW_DOCUMENTATION", False)
@click.command()
def get_images():
    logger.info("Discovering images from your gitlab-ci yml.")

def document():
    import click
import pathlib
import importlib

md_base_template = """
# {command_name}

{description}

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


def recursive_help(cmd, parent=None):
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)

    yield {"command": cmd, "help": cmd.get_help(ctx), "parent": parent.info_name if parent else '',
           "usage": cmd.get_usage(ctx),
           "params": cmd.get_params(ctx),
           "options": cmd.collect_usage_pieces(ctx)}

    commands = getattr(cmd, 'commands', {})
    for sub in commands.values():
        for helpdct in recursive_help(sub, ctx):
            yield helpdct


def dump_helper(base_command, docs_dir):
    """ Dumping help usage files from Click Help files into an md """
    docs_path = pathlib.Path(docs_dir)
    for helpdct in recursive_help(base_command):
        command = helpdct.get("command")
        helptxt = helpdct.get("help")
        usage = helpdct.get("usage")
        parent = helpdct.get("parent", "") or ''
        options = {
            opt.name: {
                "usage": '\n'.join(opt.opts),
                "prompt": opt.prompt,
                "required": opt.required,
                "default": opt.default,
                "help": opt.help,
                "type": str(opt.type)
            }
            for opt in helpdct.get('params', [])
        }
        full_command = f"{str(parent) + ' ' if parent else ''}{str(command.name)}"

        md_template = md_base_template.format(
            command_name=full_command,
            description=command.help,
            usage=usage,
            options="\n".join([
                f"* `{opt_name}`{' (REQUIRED)' if opt.get('required') else ''}: \n"
                f"  * Type: {opt.get('type')} \n"
                f"  * Default: `{str(opt.get('default')).lower()}`\n"
                f"  * Usage: `{opt.get('usage')}`\n"
                "\n"
                f"  {opt.get('help') or ''}\n"
                f"\n"
                for opt_name, opt in options.items()
            ]),
            help=helptxt
        )

        if not docs_path.exists():
            # Create md file dir if needed
            docs_path.mkdir(parents=True, exist_ok=False)

        md_file_path = docs_path.joinpath(full_command.replace(' ', '-').lower() + '.md').absolute()

        # Create the file per each command
        with open(md_file_path, 'w') as md_file:
            md_file.write(md_template)

@click.group()
def cli():
    pass

@click.command('dumps')
@click.option('--baseModule', help='The base command module path to import', required=True)
@click.option('--baseCommand', help='The base command function to import', required=True)
@click.option('--docsPath', help='The docs dir path to write the md files', required=True)
def dumps(**kwargs):
    """
    # Click-md
    Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.
    """
    base_module = kwargs.get('basemodule')
    base_command = kwargs.get('basecommand')
    docs_path = kwargs.get('docspath')

    click.secho(f'Creating a new documents from {base_module}.{base_command} into {docs_path}',
                color='green')

    try:
        # Import the module
        module_ = importlib.import_module(base_module)
    except Exception as e:
        click.echo(f'Could not find module: {base_module}. Error: {str(e)}')
        return

    try:
        # Import the base command (group of command) function inside the module
        command_ = getattr(module_, base_command)
    except:
        click.echo(f'Could not find command {base_command} on module {base_module}')
        return

    try:
        dump_helper(command_, docs_dir=docs_path)
        click.secho(f'Created docs under {docs_path}', color='green')
    except Exception as e:
        click.secho(f'Dumps command failed: {str(e)}', color='red')
        raise

    return

click.group()
@click.command()
@click.option(
    "--detailed",
    required=False,
    help="Will include workflow and rules from jobs.",
    is_flag=True,
    default=False
)
@click.option(
    "--dry-mode",
    "-d",
    "DRY_MODE",
    required=False,
    help="If set will disable documentation from being written",
    is_flag=True,
    default=False
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the markdown documentation.",

    default="README.md"
)
@click.option(
    "--input-config",
    "-i",
    "GLDOCS_CONFIG_FILE",
    required=False,
    help="The Gitlab CI Input configuration file to generated documentation from.",
    default=".gitlab-ci.yml"
)

def gitlab_docs(detailed,OUTPUT_FILE,DRY_MODE,GLDOCS_CONFIG_FILE):
    """
    A command line tool to convert your gitlab-ci yml into markdown documentation.
    """

    ENABLE_WORKFLOW_DOCUMENTATION = detailed
    logger.success("Welcome to Gitlab Docs")
    update_marked_block(file_path=OUTPUT_FILE, content="\n\n")
    # <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
    bootstrap =  f"""            <h1><span class="badge text-bg-primary">GITLAB DOCS - {GLDOCS_CONFIG_FILE}</span></h1>"""
    add_between_markers(file_path=OUTPUT_FILE,content=bootstrap)
    inputs.document_inputs(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        OUTPUT_FILE=OUTPUT_FILE,
    )
    variables.document_variables(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        OUTPUT_FILE=OUTPUT_FILE,
    )
    includes.document_includes(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        DISABLE_TYPE_HEADING=False,
        OUTPUT_FILE=OUTPUT_FILE,
    )
    if ENABLE_WORKFLOW_DOCUMENTATION is True:
        workflows.document_workflows(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            OUTPUT_FILE=OUTPUT_FILE,
        )
    jobs.get_jobs(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        DISABLE_TYPE_HEADING=False,
        OUTPUT_FILE=OUTPUT_FILE,
        detailed=detailed,
    )

    # resets markdown output file and adds GITLAB DOCS closing marker
    # md_writer.gitlab_docs_reset_writer(OUTPUT_FILE=OUTPUT_FILE, MODE="CLOSING")
    logger.info(f"Successfully generated documentation for {GLDOCS_CONFIG_FILE} here: {OUTPUT_FILE}")


if __name__ == "__main__":
    gitlab_docs(obj={})
