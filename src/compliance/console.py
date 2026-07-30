"""Rich console output for compliance results and operator feedback."""

from __future__ import annotations

from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from src.compliance.models import ComplianceResult
from src.compliance.secret_redact import redact_secrets

_STATUS_STYLES = {
    "passed": "bold green",
    "failed": "bold red",
    "skipped": "bold yellow",
}

_HINTS = {
    "--create-mr requires --fix and/or --fix-policies": (
        "Run with a fix mode, e.g. `--fix --create-mr` "
        "or `--fix-policies --create-mr`."
    ),
    "--create-mr cannot be used with --dry-run": (
        "Drop `--dry-run` when creating a merge request."
    ),
    "--create-mr requires a GitLab token": (
        "Set `--token` or `GITLAB_TOKEN` to a project/personal access token "
        "with permission to create branches and merge requests "
        "(`CI_JOB_TOKEN` is not accepted for `--create-mr`)."
    ),
    "--fix cannot be used with --dry-run": (
        "Drop `--dry-run` when applying supply-chain fixes."
    ),
    "--fix requires a GitLab token": (
        "Set `--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`."
    ),
    "--fix-supply-chain cannot be used with --dry-run": (
        "Drop `--dry-run` when applying supply-chain fixes."
    ),
    "--fix-supply-chain requires a GitLab token": (
        "Set `--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`."
    ),
    "--fix-policies cannot be used with --dry-run": (
        "Drop `--dry-run` when applying policy remediations."
    ),
    "--fix-policies requires a GitLab token": (
        "Set `--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`."
    ),
    "--post-mr-comment requires a GitLab token": (
        "Set `--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`."
    ),
    "--post-mr-comment requires --mr-iid": (
        "Pass `--mr-iid` or set `CI_MERGE_REQUEST_IID`."
    ),
    "GitLab project is required": "Pass `--project` or set `CI_PROJECT_PATH`.",
    "Pipeline file not found": "Check `-p` / `--pipeline` points at an existing YAML file.",
    "GitLab API error": "Verify token scopes, project path, and network access to GitLab.",
}


def get_console(*, width: int | None = None) -> Console:
    """Return a soft-wrapping console that tracks terminal width."""
    if width is None:
        return Console(soft_wrap=True, highlight=True)
    return Console(
        soft_wrap=True,
        highlight=True,
        width=width,
        height=25,
        force_terminal=True,
    )


def _hint_for_message(message: str) -> str | None:
    for needle, hint in _HINTS.items():
        if needle in message:
            return hint
    return None


def print_error(
    message: str,
    *,
    hint: str | None = None,
    title: str = "Error",
    console: Console | None = None,
) -> None:
    """Render a red error panel with an optional hint."""
    out = console or get_console()
    safe_message = redact_secrets(message)
    resolved_hint = hint if hint is not None else _hint_for_message(safe_message)
    body = Text(safe_message, style="bold")
    if resolved_hint:
        body.append("\n\n")
        body.append("Hint: ", style="dim")
        body.append(resolved_hint)
    out.print(
        Panel(
            body,
            title=f"[bold red]{title}[/bold red]",
            border_style="red",
            padding=(1, 2),
            expand=True,
        )
    )


def print_warning(
    message: str,
    *,
    title: str = "Warning",
    console: Console | None = None,
) -> None:
    """Render a yellow warning panel."""
    out = console or get_console()
    out.print(
        Panel(
            Text(redact_secrets(message)),
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="yellow",
            padding=(0, 2),
            expand=True,
        )
    )


def print_success(
    message: str,
    *,
    title: str = "Success",
    console: Console | None = None,
) -> None:
    """Render a green success panel."""
    out = console or get_console()
    out.print(
        Panel(
            Text(redact_secrets(message), style="bold"),
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            padding=(0, 2),
            expand=True,
        )
    )


def print_info(
    message: str,
    *,
    title: str = "Info",
    console: Console | None = None,
) -> None:
    """Render a cyan info panel."""
    out = console or get_console()
    out.print(
        Panel(
            Text(redact_secrets(message)),
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
            expand=True,
        )
    )


def _summary_table(result: ComplianceResult, *, narrow: bool) -> Table:
    summary = Table(
        title="Summary",
        show_header=True,
        header_style="bold",
        expand=True,
        pad_edge=False,
    )
    summary.add_column("Status", style="cyan", overflow="fold")
    summary.add_column("Count", justify="right", no_wrap=True)
    summary.add_row("[green]Passed[/green]", str(result.passed))
    summary.add_row("[red]Failed[/red]", str(result.failed))
    summary.add_row("[yellow]Skipped[/yellow]", str(result.skipped))
    summary.add_row("[bold]Total[/bold]", str(result.scenarios))
    if not narrow:
        summary.add_row("[dim]Features[/dim]", str(result.features))
    return summary


def _scenario_table(
    result: ComplianceResult, *, width: int, failures_only: bool = False
) -> Table | None:
    if not result.scenario_results:
        return None

    narrow = width < 60
    medium = width < 100
    scenarios = Table(
        title="Scenarios" if not failures_only else "Failed scenarios",
        show_header=True,
        header_style="bold",
        expand=True,
        pad_edge=False,
        show_lines=False,
    )
    if not narrow:
        scenarios.add_column("ID", style="magenta", overflow="ellipsis", max_width=24)
    if not medium:
        scenarios.add_column("Feature", style="cyan", overflow="ellipsis", max_width=28)
    scenarios.add_column("Policy", overflow="fold")
    scenarios.add_column("Status", justify="center", no_wrap=True)

    rows_added = 0
    for scenario in result.scenario_results:
        if failures_only and scenario.status != "failed":
            continue
        style = _STATUS_STYLES.get(scenario.status, "bold white")
        policy = scenario.title or scenario.name
        row: list[str | Text] = []
        if not narrow:
            row.append(scenario.policy_id or "-")
        if not medium:
            row.append(scenario.feature)
        row.extend([policy, Text(scenario.status.upper(), style=style)])
        scenarios.add_row(*row)
        rows_added += 1
    if rows_added == 0:
        return None
    return scenarios


def _detail_panels(
    result: ComplianceResult, *, failures_only: bool = False
) -> list[Panel]:
    blocks: list[Panel] = []
    failures = [
        scenario for scenario in result.scenario_results if scenario.status == "failed"
    ]
    if failures:
        lines: list[Text] = []
        for scenario in failures:
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            entry = Text()
            entry.append(str(label), style="bold red")
            entry.append(" — ")
            entry.append(str(title))
            if scenario.description:
                entry.append("\n")
                entry.append(scenario.description, style="italic")
            if scenario.message:
                entry.append("\n")
                entry.append(redact_secrets(scenario.message), style="dim")
            lines.append(entry)
        blocks.append(
            Panel(
                Group(*lines),
                title="[bold red]Failures[/bold red]",
                border_style="red",
                padding=(1, 2),
                expand=True,
            )
        )

    if failures_only:
        return blocks

    skipped = [
        scenario for scenario in result.scenario_results if scenario.status == "skipped"
    ]
    if skipped:
        lines = []
        for scenario in skipped:
            reason = redact_secrets(
                scenario.message or "Filter did not match any entities."
            )
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            entry = Text()
            entry.append(str(label), style="yellow")
            entry.append(" — ")
            entry.append(str(title))
            entry.append("\n")
            entry.append(reason, style="dim")
            lines.append(entry)
        blocks.append(
            Panel(
                Group(*lines),
                title="[bold yellow]Skipped[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
                expand=True,
            )
        )
    return blocks


def render_compliance_console(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    *,
    command_title: str = "check",
    console: Console | None = None,
    failures_only: bool = False,
) -> None:
    """Render a width-aware Rich compliance report."""
    out = console or get_console()
    width = out.width or 80
    narrow = width < 60
    overall = "Compliance Passed" if result.success else "Compliance Failed"
    border_style = "green" if result.success else "red"
    status_style = "bold green" if result.success else "bold red"

    header = Text()
    header.append(overall, style=status_style)
    header.append("\n\n")
    header.append("Pipeline  ", style="bold")
    header.append(pipeline_file)
    header.append("\n")
    header.append("Policies  ", style="bold")
    header.append(features_dir)
    out.print(
        Panel(
            header,
            title=f"[bold]gitlab-compliance {command_title}[/bold]",
            border_style=border_style,
            padding=(1, 2),
            expand=True,
        )
    )
    out.print(_summary_table(result, narrow=narrow))

    for block in _detail_panels(result, failures_only=failures_only):
        out.print(block)

    scenarios = _scenario_table(result, width=width, failures_only=failures_only)
    if scenarios is not None:
        out.print(scenarios)

    out.print(Rule(style="dim"))
    out.print(
        Text.from_markup(
            f"[bold green]{result.passed}[/bold green] passed  ·  "
            f"[bold red]{result.failed}[/bold red] failed  ·  "
            f"[bold yellow]{result.skipped}[/bold yellow] skipped  ·  "
            f"[dim]{result.scenarios} scenarios in {result.features} features[/dim]"
        )
    )
