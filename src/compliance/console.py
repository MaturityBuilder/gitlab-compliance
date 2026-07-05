"""Rich console output for compliance results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.compliance.models import ComplianceResult

console = Console()

_STATUS_STYLES = {
    "passed": "bold green",
    "failed": "bold red",
    "skipped": "bold yellow",
}


def render_compliance_console(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
) -> None:
    overall = "Compliance Passed" if result.success else "Compliance Failed"
    border_style = "green" if result.success else "red"

    console.print(
        Panel(
            f"[bold]Pipeline:[/bold] {pipeline_file}\n"
            f"[bold]Policies:[/bold] {features_dir}",
            title=overall,
            border_style=border_style,
        )
    )

    summary = Table(title="Summary", show_header=True, header_style="bold")
    summary.add_column("Status", style="cyan")
    summary.add_column("Count", justify="right")
    summary.add_row("[green]Passed[/green]", str(result.passed))
    summary.add_row("[red]Failed[/red]", str(result.failed))
    summary.add_row("[yellow]Skipped[/yellow]", str(result.skipped))
    summary.add_row("[bold]Total[/bold]", str(result.scenarios))
    console.print(summary)

    failures = [scenario for scenario in result.scenario_results if scenario.status == "failed"]
    if failures:
        console.rule("[bold red]Failure details")
        for scenario in failures:
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            console.print(f"[bold red]{label}[/bold red] — {title}")
            if scenario.description:
                console.print(scenario.description, style="italic")
            if scenario.message:
                console.print(scenario.message, style="dim")

    skipped = [scenario for scenario in result.scenario_results if scenario.status == "skipped"]
    if skipped:
        console.rule("[bold yellow]Skipped scenarios")
        for scenario in skipped:
            reason = scenario.message or "Filter did not match any entities."
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            console.print(f"[yellow]{label}[/yellow] — {title}: {reason}")

    scenarios = Table(title="Scenarios", show_header=True, header_style="bold")
    scenarios.add_column("ID", style="magenta", no_wrap=True)
    scenarios.add_column("Feature", style="cyan", no_wrap=True)
    scenarios.add_column("Policy")
    scenarios.add_column("Status", justify="center")

    for scenario in result.scenario_results:
        style = _STATUS_STYLES.get(scenario.status, "bold white")
        scenarios.add_row(
            scenario.policy_id or "-",
            scenario.feature,
            scenario.title or scenario.name,
            Text(scenario.status.upper(), style=style),
        )

    console.print(scenarios)

    console.print()
    console.print(
        f"[bold]{result.passed} passed[/bold], "
        f"[bold]{result.failed} failed[/bold], "
        f"[bold]{result.skipped} skipped[/bold] "
        f"({result.scenarios} scenarios in {result.features} features)"
    )
