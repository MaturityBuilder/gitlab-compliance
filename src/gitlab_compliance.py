"""
gitlab-compliance entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

# Import Thirdparty Libraries
import os
import shutil
from datetime import datetime

import click

import src.gitlab_docs as _gitlab_docs
import src.modules.doc_controller as md_writer
import src.properties.includes as includes
import src.properties.inputs as inputs
import src.properties.jobs as jobs
import src.properties.variables as variables
import src.properties.workflows as workflows
from src.compliance.metadata import build_policy_catalog
from src.compliance.oci_registry import (
    DEFAULT_POLICY_DIR,
    is_oci_reference,
    pull_policies,
    push_policies,
    resolve_features_dir,
)
from src.compliance.policy_doc import render_policy_catalog
from src.compliance.render import render_compliance_report
from src.compliance.runner import run_compliance
from src.modules.command_reference import dumps
from src.modules.constants import (
    COMPLIANCE_DEFAULT_OUTPUT_FILES,
    COMPLIANCE_OUTPUT_FORMATS,
    DEFAULT_OUTPUT_FILES,
    POLICY_DOC_DEFAULT_OUTPUT_FILES,
    POLICY_DOC_OUTPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
)
from src.modules.doc_controller import (
    add_between_markers,
    remove_duplicate_headings,
    update_marked_block,
)
from src.modules.gitstrings import process_gitstrings
from src.modules.logging import logger
from src.modules.output_filters import (
    parse_exclude,
    validate_exclude_sections,
    warn_group_by_excluded,
)
from src.modules.pipeline_data import collect_pipeline_data
from src.modules.release import release_notes
from src.modules.swagger_html import render_swagger_html
from src.modules.swagger_markdown import render_swagger_markdown
from src.properties.extract_job_attribute import get_job_attribute

__all__ = [
    "DEFAULT_POLICY_DIR",
    "build_policy_catalog",
    "check",
    "document",
    "document_gitstrings",
    "dumps",
    "generate",
    "generate_html",
    "get_attributes",
    "gitlab_compliance",
    "gitlab_docs",
    "is_oci_reference",
    "policies",
    "policies_doc",
    "policies_pull",
    "policies_push",
    "pull_policies",
    "push_policies",
    "release_notes",
    "render_compliance_report",
    "resolve_features_dir",
    "run_compliance",
]


def _parse_generate_filters(exclude, group_by):
    """Parse and validate generate filter options."""
    exclude_sections, exclude_attributes = parse_exclude(exclude)
    validate_exclude_sections(exclude_sections)
    warn_group_by_excluded(group_by, exclude_attributes)
    return exclude_sections, exclude_attributes, group_by


def _generate_markdown(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    detailed=False,
    exclude_sections=None,
    exclude_attributes=None,
    group_by=None,
    max_include_depth=None,
):
    ENABLE_WORKFLOW_DOCUMENTATION = detailed
    exclude_sections = exclude_sections or set()
    update_marked_block(file_path=OUTPUT_FILE, content="\n")
    bootstrap = f"""## GITLAB COMPLIANCE - {GLDOCS_CONFIG_FILE}"""
    add_between_markers(file_path=OUTPUT_FILE, content=bootstrap)
    if "inputs" not in exclude_sections:
        inputs.document_inputs(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            OUTPUT_FILE=OUTPUT_FILE,
        )
    if "variables" not in exclude_sections:
        variables.document_variables(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            OUTPUT_FILE=OUTPUT_FILE,
        )
    if "includes" not in exclude_sections:
        includes.document_includes(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            DISABLE_TYPE_HEADING=False,
            OUTPUT_FILE=OUTPUT_FILE,
            max_include_depth=max_include_depth,
        )
    if ENABLE_WORKFLOW_DOCUMENTATION is True and "workflow" not in exclude_sections:
        workflows.document_workflows(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            OUTPUT_FILE=OUTPUT_FILE,
        )
    if "jobs" not in exclude_sections:
        pipeline_data = collect_pipeline_data(
            config_file=GLDOCS_CONFIG_FILE,
            detailed=detailed,
            max_include_depth=max_include_depth,
            exclude_sections=exclude_sections,
            exclude_attributes=exclude_attributes,
            group_by=group_by,
        )
        jobs.render_jobs_from_pipeline(
            OUTPUT_FILE=OUTPUT_FILE,
            pipeline_data=pipeline_data,
            detailed=detailed,
        )


def _generate_html(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    detailed=False,
    exclude_sections=None,
    exclude_attributes=None,
    group_by=None,
    max_include_depth=None,
):
    pipeline_data = collect_pipeline_data(
        config_file=GLDOCS_CONFIG_FILE,
        detailed=detailed,
        max_include_depth=max_include_depth,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
    )
    html_output = render_swagger_html(pipeline_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        output_file.write(html_output)


def _generate_swagger_markdown(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    detailed=False,
    exclude_sections=None,
    exclude_attributes=None,
    group_by=None,
    max_include_depth=None,
):
    pipeline_data = collect_pipeline_data(
        config_file=GLDOCS_CONFIG_FILE,
        detailed=detailed,
        max_include_depth=max_include_depth,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
    )
    markdown_output = render_swagger_markdown(pipeline_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        output_file.write(markdown_output)


def _resolve_output_file(output_format, output_file):
    if output_file:
        return output_file
    return DEFAULT_OUTPUT_FILES[output_format]


_LEGACY_CLI_NAME = "gitlab-docs"


class _DualBrandCliGroup(click.Group):
    """Shared CLI group; warns when invoked via the legacy ``gitlab-compliance`` script name."""

    _LEGACY_NOTICE = (
        "Note: `gitlab-docs` is deprecated in favor of `gitlab-compliance`. "
        "The `gitlab-docs` command will be removed in a future release."
    )

    def _emit_legacy_notice(self, ctx) -> None:
        if ctx.info_name == _LEGACY_CLI_NAME:
            click.secho(self._LEGACY_NOTICE, fg="yellow", err=True)

    def invoke(self, ctx):
        self._emit_legacy_notice(ctx)
        return super().invoke(ctx)

    def format_help(self, ctx, formatter):
        if ctx.info_name == _LEGACY_CLI_NAME:
            formatter.write(click.style(f"{self._LEGACY_NOTICE}\n\n", fg="yellow"))
        return super().format_help(ctx, formatter)


@click.group(cls=_DualBrandCliGroup)
def gitlab_compliance():
    """
    GitLab CI compliance and pipeline documentation.

    Run Gherkin policies with ``check`` (and optional GitLab API settings),
    manage policy bundles with ``policies``, or generate Markdown/HTML
    documentation from pipeline YAML.
    """
    pass


# Backward-compatible alias for imports and ``python -m src.gitlab_compliance``.
gitlab_docs = gitlab_compliance


# ENABLE_WORKFLOW_DOCUMENTATION = os.getenv("ENABLE_WORKFLOW_DOCUMENTATION", False)
@click.command()
@click.option(
    "--attributes",
    "-a",
    "attributes",
    required=False,
    help="Pass a comma seperated list of gitlab ci yml attributes",
    default="README.md",
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the markdown documentation.",
    default="README.md",
)
@click.option(
    "--input-config",
    "-i",
    "GLDOCS_CONFIG_FILE",
    required=False,
    help="The Gitlab CI Input configuration file to generated documentation from.",
    default=".gitlab-ci.yml",
)
@click.option(
    "--json",
    "-j",
    "json_format",
    required=False,
    default=False,
    type=bool,
    help="Return results in json format.",
)
def get_attributes(OUTPUT_FILE, GLDOCS_CONFIG_FILE, attributes, json_format):
    """
    Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
    Args:
        OUTPUT_FILE (_type_): _description_
        GLDOCS_CONFIG_FILE (_type_): _description_
        attributes (_type_): _description_
        json (_type_): _description_
    """
    logger.info(f"Discovering attributes {attributes} from your gitlab-ci yml.")

    get_job_attribute(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
        DISABLE_TITLE=False,
        DISABLE_TYPE_HEADING=False,
        OUTPUT_FILE=OUTPUT_FILE,
        attributes=attributes,
        json_format=json_format,
    )


@click.command()
@click.option(
    "--detailed",
    required=False,
    help="Will include workflow and rules from jobs.",
    is_flag=True,
    default=False,
)
@click.option(
    "--format",
    "-f",
    "output_format",
    required=False,
    type=click.Choice(SUPPORTED_OUTPUT_FORMATS, case_sensitive=False),
    default="markdown",
    help="Output format for generated documentation.",
)
@click.option(
    "--dry-mode",
    "-d",
    "DRY_MODE",
    required=False,
    help="If set will disable documentation from being written",
    is_flag=True,
    default=False,
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the generated documentation.",
    default=None,
)
@click.option(
    "--input-config",
    "-i",
    "GLDOCS_CONFIG_FILE",
    required=False,
    help="The Gitlab CI Input configuration file to generated documentation from.",
    default=".gitlab-ci.yml",
)
@click.option(
    "--exclude",
    "-x",
    "exclude",
    required=False,
    default=None,
    help=(
        "Comma-separated sections or job attributes to omit from output. "
        "Sections: inputs, variables, includes, workflow, jobs, container_images."
    ),
)
@click.option(
    "--group-by",
    "-g",
    "group_by",
    required=False,
    default=None,
    help="Group jobs in the Jobs section by this job attribute (e.g. stage).",
)
@click.option(
    "--max-include-depth",
    "max_include_depth",
    type=int,
    default=None,
    help="Max local include nesting depth from the root file (omit for unlimited).",
)
def generate(
    detailed,
    output_format,
    OUTPUT_FILE,
    DRY_MODE,
    GLDOCS_CONFIG_FILE,
    exclude,
    group_by,
    max_include_depth,
):
    """
    Will scan through your gitlab-ci yml and build documentation from the yml.
    """
    output_format = output_format.lower()
    OUTPUT_FILE = _resolve_output_file(output_format, OUTPUT_FILE)
    logger.success("Welcome to Gitlab Compliance")

    try:
        exclude_sections, exclude_attributes, group_by = _parse_generate_filters(
            exclude, group_by
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if DRY_MODE:
        logger.info(
            f"Dry mode enabled; skipping write for {GLDOCS_CONFIG_FILE} ({output_format})"
        )
        return

    gen_kwargs = dict(
        OUTPUT_FILE=OUTPUT_FILE,
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
        detailed=detailed,
        exclude_sections=exclude_sections,
        exclude_attributes=exclude_attributes,
        group_by=group_by,
        max_include_depth=max_include_depth,
    )

    if output_format == "html":
        _generate_html(**gen_kwargs)
    elif output_format == "swagger-markdown":
        _generate_swagger_markdown(**gen_kwargs)
    else:
        _generate_markdown(**gen_kwargs)

    logger.info(
        f"Successfully generated {output_format} documentation for "
        f"{GLDOCS_CONFIG_FILE} here: {OUTPUT_FILE}"
    )


@click.command(
    hidden=True,
    deprecated=True,
    help="Deprecated: use `generate --format html` instead.",
)
@click.option(
    "--detailed",
    required=False,
    help="Will include workflow and rules from jobs.",
    is_flag=True,
    default=False,
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the HTML documentation.",
    default="gitlab-compliance.html",
)
@click.option(
    "--input-config",
    "-i",
    "GLDOCS_CONFIG_FILE",
    required=False,
    help="The Gitlab CI Input configuration file to generated documentation from.",
    default=".gitlab-ci.yml",
)
def generate_html(detailed, OUTPUT_FILE, GLDOCS_CONFIG_FILE):
    """
    Generate a Swagger-style HTML page from your gitlab-ci yml.
    """
    ctx = click.get_current_context(silent=True)
    if ctx is not None:
        ctx.invoke(
            generate,
            detailed=detailed,
            output_format="html",
            OUTPUT_FILE=OUTPUT_FILE,
            DRY_MODE=False,
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
        )
        return

    OUTPUT_FILE = _resolve_output_file("html", OUTPUT_FILE)
    logger.success("Welcome to GitLab Docs HTML")
    _generate_html(
        OUTPUT_FILE=OUTPUT_FILE,
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
        detailed=detailed,
    )
    logger.info(
        f"Successfully generated html documentation for "
        f"{GLDOCS_CONFIG_FILE} here: {OUTPUT_FILE}"
    )


def _resolve_compliance_output(output_format, output_file):
    if output_file:
        return output_file
    if output_format in COMPLIANCE_DEFAULT_OUTPUT_FILES:
        return COMPLIANCE_DEFAULT_OUTPUT_FILES[output_format]
    return None


def _resolve_policies_dir(
    features_dir: str, policy_cache_dir: str | None = None
) -> tuple[str, str]:
    if os.path.isdir(features_dir):
        resolved = os.path.abspath(features_dir)
        return resolved, resolved
    resolved = _gitlab_docs.resolve_features_dir(
        features_dir, cache_dir=policy_cache_dir
    )
    return resolved, features_dir


@click.command("check")
@click.option(
    "--features",
    "-f",
    "features_dir",
    required=True,
    help="Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).",
)
@click.option(
    "--pipeline",
    "-p",
    "pipeline_file",
    required=False,
    default=".gitlab-ci.yml",
    help="Path to the GitLab CI pipeline YAML file.",
)
@click.option(
    "--format",
    "output_format",
    required=False,
    type=click.Choice(COMPLIANCE_OUTPUT_FORMATS, case_sensitive=False),
    default="console",
    help="Output format for the compliance report.",
)
@click.option(
    "--output-file",
    "-o",
    "output_file",
    required=False,
    default=None,
    help="Write rendered report to this file (markdown, html, mr-comment).",
)
@click.option(
    "--include-nested/--no-include-nested",
    default=True,
    help="Resolve nested local include files into the compliance stash.",
)
@click.option(
    "--max-include-depth",
    "max_include_depth",
    type=int,
    default=None,
    help="Max local include nesting depth from the root file (omit for unlimited).",
)
@click.option(
    "--gitlab-url",
    default=None,
    help="GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).",
)
@click.option(
    "--token",
    default=None,
    help="GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).",
)
@click.option(
    "--project",
    default=None,
    help="GitLab project path or ID for API-backed policy checks.",
)
@click.option(
    "--group",
    default=None,
    help="GitLab group path or ID for API-backed policy checks.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Fail API-backed scenarios when connection info is missing (default: skip).",
)
@click.option(
    "--update",
    is_flag=True,
    default=False,
    help="Pull the latest policies from an OCI registry before running checks.",
)
@click.option(
    "--policy-cache-dir",
    default=None,
    help="Directory used when pulling OCI policy bundles (default: system temp).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Parse and list scenarios without asserting.",
)
@click.option(
    "--fix-supply-chain",
    is_flag=True,
    default=False,
    help="Auto-fix outdated include refs and pin container images to sha256 digests.",
)
@click.option(
    "--fix-policies",
    is_flag=True,
    default=False,
    help=(
        "After an initial policy run, apply allowlisted BDD remediations "
        "(see docs/usage/fix-policies.md), then re-check."
    ),
)
@click.option(
    "--create-mr",
    is_flag=True,
    default=False,
    help=(
        "After --fix-supply-chain and/or --fix-policies, commit changed files "
        "and open a GitLab merge request (needs a project/personal access token; "
        "CI_JOB_TOKEN is usually insufficient; failures exit 2 after the report)."
    ),
)
@click.option(
    "--post-mr-comment",
    is_flag=True,
    default=False,
    help="Post the compliance mr-comment body to a GitLab merge request.",
)
@click.option(
    "--mr-iid",
    type=int,
    default=None,
    help="Merge request IID for --post-mr-comment (default: CI_MERGE_REQUEST_IID).",
)
@click.option(
    "--mr-branch",
    default=None,
    help=(
        "Source branch for --create-mr "
        "(default: gitlab-compliance/supply-chain-fix). "
        "Reuses an open MR for this branch, or reopens a closed one."
    ),
)
@click.option(
    "--mr-target-branch",
    default=None,
    help="Target branch for --create-mr (default: project default branch).",
)
@click.option(
    "--mr-comment-file",
    default=None,
    help="Optional pre-rendered markdown file to post with --post-mr-comment.",
)
@click.option(
    "--with-builtin",
    is_flag=True,
    default=False,
    help="Also run bundled baseline policies shipped with gitlab-compliance.",
)
def check(
    features_dir,
    pipeline_file,
    output_format,
    output_file,
    include_nested,
    max_include_depth,
    gitlab_url,
    token,
    project,
    group,
    strict,
    update,
    policy_cache_dir,
    dry_run,
    fix_supply_chain,
    fix_policies,
    create_mr,
    post_mr_comment,
    mr_iid,
    mr_branch,
    mr_target_branch,
    mr_comment_file,
    with_builtin,
):
    """
    Run Gherkin compliance policies against GitLab CI YAML and optional API settings.
    """
    output_format = output_format.lower()

    from src.compliance.console import print_error, print_success

    if (
        update
        and _gitlab_docs.is_oci_reference(features_dir)
        and policy_cache_dir
        and os.path.isdir(policy_cache_dir)
    ):
        shutil.rmtree(policy_cache_dir)

    try:
        result = _gitlab_docs.run_compliance(
            features_dir=features_dir,
            pipeline_file=pipeline_file,
            include_nested=include_nested,
            max_include_depth=max_include_depth,
            gitlab_url=gitlab_url,
            token=token,
            project=project,
            group=group,
            strict=strict,
            dry_run=dry_run,
            output_format=output_format,
            policies_source=features_dir,
            policy_cache_dir=policy_cache_dir,
            fix_supply_chain=fix_supply_chain,
            fix_policies=fix_policies,
            with_builtin=with_builtin,
            create_mr=create_mr,
            post_mr_comment=post_mr_comment,
            mr_iid=mr_iid,
            mr_branch=mr_branch,
            mr_target_branch=mr_target_branch,
            mr_comment_file=mr_comment_file,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print_error(str(exc))
        raise SystemExit(2) from exc

    if output_format != "console":
        report = _gitlab_docs.render_compliance_report(
            result=result,
            pipeline_file=pipeline_file,
            features_dir=features_dir,
            output_format=output_format,
        )
        target = _resolve_compliance_output(output_format, output_file)
        if target:
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(report)
            print_success(
                f"Compliance report written to `{target}`",
                title="Report written",
            )
        else:
            click.echo(report)

        if result.success:
            print_success(
                f"Compliance passed for `{pipeline_file}`",
                title="Complete",
            )
        else:
            print_error(
                f"Compliance failed for `{pipeline_file}`",
                title="Complete",
                hint="Review the report, then re-run after fixes.",
            )
    raise SystemExit(result.exit_code)


def _resolve_policy_doc_output(output_format, output_file):
    if output_file:
        return output_file
    if output_format in POLICY_DOC_DEFAULT_OUTPUT_FILES:
        return POLICY_DOC_DEFAULT_OUTPUT_FILES[output_format]
    return None


@click.group()
def policies():
    """Manage compliance policy bundles (catalog, OCI push/pull)."""
    pass


@policies.command("doc")
@click.option(
    "--features",
    "-f",
    "features_dir",
    required=True,
    help="Directory containing compliance policy .feature files.",
)
@click.option(
    "--format",
    "output_format",
    required=False,
    type=click.Choice(POLICY_DOC_OUTPUT_FORMATS, case_sensitive=False),
    default="markdown",
    help="Output format for the policy catalog.",
)
@click.option(
    "--output-file",
    "-o",
    "output_file",
    required=False,
    default=None,
    help="Write the policy catalog to this file.",
)
def policies_doc(features_dir, output_format, output_file):
    """
    Generate a searchable policy catalog from Conftest-style # METADATA annotations.
    """
    output_format = output_format.lower()
    resolved_dir, _source = _resolve_policies_dir(features_dir)
    catalog = _gitlab_docs.build_policy_catalog(resolved_dir)
    report = render_policy_catalog(catalog, _source, output_format)
    target = _resolve_policy_doc_output(output_format, output_file)
    if target:
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(report)
        logger.info(f"Policy catalog written to {target}")
    else:
        click.echo(report)


@policies.command("push")
@click.option(
    "--features",
    "-f",
    "features_dir",
    required=True,
    help="Directory containing compliance policy .feature files to publish.",
)
@click.argument("target")
def policies_push(features_dir, target):
    """
    Push a compliance policy bundle to an OCI registry (Conftest-style).
    """
    digest = _gitlab_docs.push_policies(features_dir, target)
    logger.success(f"Pushed policy bundle to {target}")
    if digest:
        logger.info(f"Digest: {digest}")


@policies.command("pull")
@click.argument("target")
@click.option(
    "--output-dir",
    "-o",
    "output_dir",
    default=_gitlab_docs.DEFAULT_POLICY_DIR,
    show_default=True,
    help="Directory to extract pulled policies into.",
)
def policies_pull(target, output_dir):
    """
    Pull a compliance policy bundle from an OCI registry.
    """
    pulled_to = _gitlab_docs.pull_policies(target, output_dir=output_dir)
    logger.success(f"Pulled policies to {pulled_to}")


@click.group()
def document():
    """Generate documentation from inline template YAML (gitstrings)."""
    pass


@document.command("gitstrings")
@click.option(
    "-i",
    "--input-file",
    "input_file",
    default="README.md",
    show_default=True,
    help="Markdown or CI YAML (.yml) file with gitstrings decorators or fenced snippets.",
)
@click.option(
    "-o",
    "--output-file",
    "--output",
    "output_file",
    default=None,
    help="Markdown file for gitstrings marker updates. When set, all fragments write here and # @output in YAML is ignored.",
)
@click.option(
    "--dry-mode",
    "-d",
    "dry_mode",
    is_flag=True,
    default=False,
    help="Log updates without writing files.",
)
@click.option(
    "--keep-source/--no-keep-source",
    "keep_source",
    default=True,
    show_default=True,
    help="Include collapsible source YAML in the generated marker block.",
)
@click.option(
    "--include-nested",
    "include_nested",
    is_flag=True,
    default=False,
    help=(
        "Walk nested local: includes on disk when documenting @render includes "
        "(-i must be .yml). Does not fetch project, component, remote, or template trees."
    ),
)
@click.option(
    "--max-include-depth",
    "max_include_depth",
    type=int,
    default=None,
    help="Max local include nesting depth from the root file (omit for unlimited).",
)
def document_gitstrings(
    input_file, output_file, dry_mode, keep_source, include_nested, max_include_depth
):
    """
    Render gitstrings documentation from CI YAML decorators or markdown fences.
    """
    if dry_mode:
        logger.info("Dry mode enabled; gitstrings marker updates will be logged only.")
    written = process_gitstrings(
        input_file,
        output_file,
        dry=dry_mode,
        keep_source=keep_source,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
    )
    if written:
        for path in written:
            logger.info(f"Gitstrings documentation updated: {path}")
    else:
        logger.info("No gitstrings output files were updated.")


gitlab_compliance.add_command(get_attributes)
gitlab_compliance.add_command(dumps)
gitlab_compliance.add_command(generate)
gitlab_compliance.add_command(generate_html)
gitlab_compliance.add_command(check)
gitlab_compliance.add_command(policies)
gitlab_compliance.add_command(document)
gitlab_compliance.add_command(release_notes)
if __name__ == "__main__":  # pragma: no cover
    gitlab_compliance(obj={})
