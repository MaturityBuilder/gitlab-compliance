"""Modern Rich terminal UX for ``gitlab-compliance lock``.

Inspired by contemporary CI inventory CLIs (progress, health banner, PBOM-style
tables, actionable next steps) while staying script-friendly with quiet/JSON
modes.
"""

from __future__ import annotations

import json
from typing import Any, Callable, TypeVar

from rich import box
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from src.compliance.console import get_console
from src.compliance.lockfile import summarize_inventory
from src.compliance.secret_redact import redact_secrets

T = TypeVar("T")

_SHORT_FP = 16


def _short_fingerprint(fingerprint: str) -> str:
    value = fingerprint.removeprefix("sha256:")
    if len(value) <= _SHORT_FP:
        return fingerprint
    return f"sha256:{value[:12]}…{value[-8:]}"


def _inventory_health(inventory: dict[str, Any]) -> dict[str, Any]:
    """Score inventory completeness (not supply-chain maturity).

    Declared components/templates count as inventoried even when offline
    resolution cannot fetch their bodies. Digest pinning is reported as a
    separate pin-rate signal and only slightly boosts the letter.
    """
    includes = list(inventory.get("includes") or [])
    images = list(inventory.get("images") or [])
    unresolved = list(inventory.get("unresolved") or [])
    external = list(inventory.get("externalSteps") or [])

    resolved_includes = sum(1 for item in includes if item.get("resolved"))
    declared_external = sum(
        1 for item in includes if item.get("type") in {"component", "template"}
    )
    inventoried_includes = resolved_includes + declared_external
    # Avoid double-counting resolved components (rare).
    inventoried_includes = min(inventoried_includes, len(includes))
    pinned_images = sum(1 for item in images if item.get("digest"))
    include_total = len(includes)
    image_total = len(images)

    include_coverage = (
        100.0 if include_total == 0 else (inventoried_includes / include_total) * 100.0
    )
    # Successful parse of the pipeline is a strong baseline for lock UX.
    score = 55.0 + (include_coverage * 0.35)
    if image_total:
        pin_rate = (pinned_images / image_total) * 100.0
        score += pin_rate * 0.10
    else:
        pin_rate = 100.0
        score += 10.0

    fetch_gaps = [
        item
        for item in unresolved
        if str(item.get("reason") or "")
        not in {"unsupported_type", "include_nested_disabled"}
    ]
    if fetch_gaps:
        score = max(0.0, score - min(30.0, len(fetch_gaps) * 8.0))

    score = min(100.0, score)
    if score >= 90:
        letter, tone = "A", "green"
    elif score >= 75:
        letter, tone = "B", "green"
    elif score >= 60:
        letter, tone = "C", "yellow"
    elif score >= 40:
        letter, tone = "D", "yellow"
    else:
        letter, tone = "E", "red"

    return {
        "score": round(score, 1),
        "letter": letter,
        "tone": tone,
        "resolvedIncludes": resolved_includes,
        "inventoriedIncludes": inventoried_includes,
        "includeTotal": include_total,
        "pinnedImages": pinned_images,
        "pinRate": round(pin_rate, 1),
        "imageTotal": image_total,
        "unresolved": len(unresolved),
        "externalSteps": len(external),
    }


def _metric_panel(label: str, value: str, *, style: str = "cyan") -> Panel:
    body = Text()
    body.append(str(value), style=f"bold {style}")
    body.append("\n")
    body.append(label, style="dim")
    return Panel(body, box=box.ROUNDED, border_style=style, padding=(0, 1), expand=True)


def _health_banner(health: dict[str, Any]) -> Panel:
    tone = health["tone"]
    bar_width = 24
    filled = int(round((health["score"] / 100.0) * bar_width))
    bar = "█" * filled + "░" * (bar_width - filled)

    body = Text()
    body.append("Inventory health  ", style="bold")
    body.append(health["letter"], style=f"bold {tone}")
    body.append(f"  {health['score']:.0f}/100\n", style=tone)
    body.append(bar, style=tone)
    body.append("\n\n", style=tone)
    body.append(
        f"{health['inventoriedIncludes']}/{health['includeTotal']} includes inventoried  ·  "
        f"{health['pinnedImages']}/{health['imageTotal']} images digest-pinned "
        f"({health['pinRate']:.0f}%)  ·  "
        f"{health['unresolved']} unresolved",
        style="dim",
    )
    return Panel(
        body,
        title="[bold]Coverage[/bold]",
        border_style=tone,
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True,
    )


def _header_panel(
    *,
    title: str,
    outcome: str,
    outcome_style: str,
    pipeline_file: str,
    lock_file: str,
    fingerprint: str,
) -> Panel:
    body = Text()
    body.append(outcome, style=outcome_style)
    body.append("\n\n")
    body.append("Pipeline     ", style="bold")
    body.append(pipeline_file)
    body.append("\n")
    body.append("Lock file    ", style="bold")
    body.append(lock_file)
    body.append("\n")
    body.append("Fingerprint  ", style="bold")
    body.append(_short_fingerprint(fingerprint), style="magenta")
    return Panel(
        body,
        title=f"[bold]gitlab-compliance lock · {title}[/bold]",
        border_style=outcome_style.replace("bold ", ""),
        box=box.HEAVY,
        padding=(1, 2),
        expand=True,
    )


def _counts_columns(counts: dict[str, int], health: dict[str, Any]) -> Columns:
    unresolved_style = "red" if counts.get("unresolved", 0) else "green"
    return Columns(
        [
            _metric_panel("Jobs", str(counts.get("jobs", 0)), style="cyan"),
            _metric_panel("Includes", str(counts.get("includes", 0)), style="blue"),
            _metric_panel("Images", str(counts.get("images", 0)), style="magenta"),
            _metric_panel(
                "External steps",
                str(counts.get("externalSteps", 0)),
                style="yellow",
            ),
            _metric_panel(
                "Unresolved",
                str(counts.get("unresolved", 0)),
                style=unresolved_style,
            ),
            _metric_panel("Health", health["letter"], style=health["tone"]),
        ],
        equal=True,
        expand=True,
    )


def _includes_table(inventory: dict[str, Any], *, verbose: bool) -> Table | None:
    includes = list(inventory.get("includes") or [])
    if not includes:
        return None
    table = Table(
        title="Includes",
        box=box.SIMPLE_HEAVY,
        header_style="bold",
        expand=True,
        show_lines=False,
        pad_edge=False,
    )
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Reference", overflow="fold")
    table.add_column("Ref", style="magenta", overflow="ellipsis", max_width=18)
    table.add_column("Status", justify="center", no_wrap=True)
    if verbose:
        table.add_column("Hash", style="dim", overflow="ellipsis", max_width=22)

    limit = len(includes) if verbose else min(8, len(includes))
    for item in includes[:limit]:
        status = (
            Text("RESOLVED", style="bold green")
            if item.get("resolved")
            else Text("PENDING", style="bold yellow")
        )
        ref = str(item.get("project") or item.get("id") or "-")
        row = [
            str(item.get("type", "")),
            ref,
            str(item.get("ref") or "-"),
            status,
        ]
        if verbose:
            digest = item.get("contentHash") or "-"
            row.append(str(digest).removeprefix("sha256:")[:16])
        table.add_row(*row)
    if not verbose and len(includes) > limit:
        table.caption = f"[dim]+{len(includes) - limit} more — pass --verbose[/dim]"
    return table


def _images_table(inventory: dict[str, Any], *, verbose: bool) -> Table | None:
    images = list(inventory.get("images") or [])
    if not images:
        return None
    table = Table(
        title="Images & services",
        box=box.SIMPLE_HEAVY,
        header_style="bold",
        expand=True,
        pad_edge=False,
    )
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Job", overflow="ellipsis", max_width=20)
    table.add_column("Image", overflow="fold")
    table.add_column("Pin", justify="center", no_wrap=True)

    limit = len(images) if verbose else min(8, len(images))
    for item in images[:limit]:
        pinned = bool(item.get("digest"))
        pin = (
            Text("DIGEST", style="bold green")
            if pinned
            else Text("TAG", style="bold yellow")
        )
        table.add_row(
            str(item.get("source", "")),
            str(item.get("parentJob", "")),
            str(item.get("image", "")),
            pin,
        )
    if not verbose and len(images) > limit:
        table.caption = f"[dim]+{len(images) - limit} more — pass --verbose[/dim]"
    return table


def _external_tree(inventory: dict[str, Any]) -> Tree | None:
    steps = list(inventory.get("externalSteps") or [])
    if not steps:
        return None
    tree = Tree("[bold]External steps[/bold]", guide_style="dim")
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for step in steps:
        by_kind.setdefault(str(step.get("kind", "other")), []).append(step)
    for kind in sorted(by_kind):
        branch = tree.add(f"[cyan]{kind}[/cyan] ([dim]{len(by_kind[kind])}[/dim])")
        for step in by_kind[kind][:6]:
            label = step.get("id") or step.get("project") or step.get("job") or "?"
            branch.add(Text(str(label), style="white"))
        if len(by_kind[kind]) > 6:
            branch.add(Text(f"+{len(by_kind[kind]) - 6} more", style="dim"))
    return tree


def _unresolved_panel(inventory: dict[str, Any]) -> Panel | None:
    unresolved = list(inventory.get("unresolved") or [])
    if not unresolved:
        return None
    lines: list[Text] = []
    for item in unresolved[:10]:
        entry = Text()
        entry.append(str(item.get("type") or "include"), style="yellow")
        entry.append("  ")
        entry.append(str(item.get("reference") or "-"))
        reason = item.get("reason") or "unresolved"
        entry.append(f"  ·  {reason}", style="dim")
        lines.append(entry)
    if len(unresolved) > 10:
        lines.append(Text(f"+{len(unresolved) - 10} more", style="dim"))
    return Panel(
        Group(*lines),
        title="[bold yellow]Unresolved[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True,
    )


def _next_steps(
    *,
    command: str,
    matches: bool | None,
    pipeline_file: str,
    lock_file: str,
) -> Panel:
    lines = Text()
    if command in {"generate", "update"}:
        lines.append("1. ", style="bold cyan")
        lines.append(f"Commit {lock_file}\n")
        lines.append("2. ", style="bold cyan")
        lines.append("Gate compliance with rules:changes on the lock file\n")
        lines.append("3. ", style="bold cyan")
        lines.append(
            f"Verify in CI: gitlab-compliance lock verify -p {pipeline_file} -l {lock_file}"
        )
    elif command == "verify" and matches:
        lines.append("Inventory matches. ", style="green")
        lines.append("Safe to skip heavy compliance work when rules allow.")
    else:
        lines.append("1. ", style="bold cyan")
        lines.append(
            f"Refresh: gitlab-compliance lock update -p {pipeline_file} -l {lock_file}\n"
        )
        lines.append("2. ", style="bold cyan")
        lines.append("Review the lock diff, then commit\n")
        lines.append("3. ", style="bold cyan")
        lines.append("Re-run verify in CI")
    return Panel(
        lines,
        title="[bold]Next steps[/bold]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True,
    )


def _drift_panel(expected: str, actual: str) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True, pad_edge=False)
    table.add_column("Side", style="bold", no_wrap=True)
    table.add_column("Fingerprint", style="magenta", overflow="fold")
    table.add_row("Lock file", expected)
    table.add_row("Current", actual)
    return Panel(
        table,
        title="[bold red]Drift detected[/bold red]",
        border_style="red",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True,
    )


def run_with_progress(
    label: str,
    work: Callable[[], T],
    *,
    console: Console | None = None,
    quiet: bool = False,
) -> T:
    """Run work under a spinner/progress UI when the console is a TTY."""
    out = console or get_console()
    if quiet or not out.is_terminal:
        return work()

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]{task.description}[/bold]"),
        BarColumn(bar_width=24, complete_style="cyan", finished_style="green"),
        TimeElapsedColumn(),
        console=out,
        transient=True,
    ) as progress:
        task_id = progress.add_task(label, total=None)
        try:
            result = work()
        finally:
            progress.update(task_id, completed=1)
        return result


def render_lock_report(
    *,
    command: str,
    lockfile: dict[str, Any],
    pipeline_file: str,
    lock_file: str,
    matches: bool | None = None,
    expected_fingerprint: str | None = None,
    actual_fingerprint: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
    as_json: bool = False,
    console: Console | None = None,
) -> None:
    """Render generate/update/verify results with a modern Rich report."""
    out = console or get_console()
    inventory = lockfile.get("inventory") or {}
    fingerprint = str(
        actual_fingerprint or lockfile.get("fingerprint") or expected_fingerprint or ""
    )
    counts = summarize_inventory(inventory)
    health = _inventory_health(inventory)

    if as_json:
        payload = {
            "command": command,
            "pipelineFile": pipeline_file,
            "lockFile": lock_file,
            "fingerprint": fingerprint,
            "matches": matches,
            "expectedFingerprint": expected_fingerprint,
            "actualFingerprint": actual_fingerprint or fingerprint,
            "counts": counts,
            "health": health,
            "inventory": inventory if verbose else None,
        }
        out.print_json(data=payload)
        return

    if quiet:
        if command == "verify" and matches is False:
            out.print(actual_fingerprint or fingerprint)
            return
        out.print(fingerprint)
        return

    if command in {"generate", "update"}:
        outcome = "Inventory locked"
        outcome_style = "bold green"
        title = "generate" if command == "generate" else "update"
    elif matches:
        outcome = "Lock verified"
        outcome_style = "bold green"
        title = "verify"
    else:
        outcome = "Lock drift"
        outcome_style = "bold red"
        title = "verify"

    out.print(
        _header_panel(
            title=title,
            outcome=outcome,
            outcome_style=outcome_style,
            pipeline_file=pipeline_file,
            lock_file=lock_file,
            fingerprint=fingerprint,
        )
    )
    out.print(_counts_columns(counts, health))
    out.print(_health_banner(health))

    if matches is False and expected_fingerprint and actual_fingerprint:
        out.print(_drift_panel(expected_fingerprint, actual_fingerprint))

    includes = _includes_table(inventory, verbose=verbose)
    if includes is not None:
        out.print(includes)

    images = _images_table(inventory, verbose=verbose)
    if images is not None:
        out.print(images)

    tree = _external_tree(inventory)
    if tree is not None:
        out.print(tree)

    unresolved = _unresolved_panel(inventory)
    if unresolved is not None:
        out.print(unresolved)

    out.print(
        _next_steps(
            command=command,
            matches=matches,
            pipeline_file=pipeline_file,
            lock_file=lock_file,
        )
    )
    out.print(Rule(style="dim"))
    footer = Text.from_markup(
        f"[bold green]{counts['jobs']}[/bold green] jobs  ·  "
        f"[bold blue]{counts['includes']}[/bold blue] includes  ·  "
        f"[bold magenta]{counts['images']}[/bold magenta] images  ·  "
        f"[bold yellow]{counts['externalSteps']}[/bold yellow] external  ·  "
        f"health [bold {health['tone']}]{health['letter']}[/bold {health['tone']}]"
    )
    out.print(footer)


def render_fingerprint_line(
    fingerprint: str,
    *,
    dotenv_file: str | None = None,
    quiet: bool = False,
    as_json: bool = False,
    console: Console | None = None,
) -> None:
    """Render fingerprint output for scripting or a small Rich card."""
    out = console or get_console()
    if as_json:
        out.print_json(
            data={
                "fingerprint": fingerprint,
                "dotenvFile": dotenv_file,
            }
        )
        return
    if quiet or not out.is_terminal:
        out.print(fingerprint)
        if dotenv_file:
            out.print(f"# wrote {dotenv_file}", style="dim")
        return

    body = Text()
    body.append(_short_fingerprint(fingerprint), style="bold magenta")
    body.append("\n")
    body.append(fingerprint, style="dim")
    if dotenv_file:
        body.append("\n\n")
        body.append("Dotenv  ", style="bold")
        body.append(dotenv_file)
    out.print(
        Panel(
            body,
            title="[bold]Fingerprint[/bold]",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(1, 2),
            expand=True,
        )
    )


def render_lock_error(
    message: str,
    *,
    hint: str | None = None,
    console: Console | None = None,
) -> None:
    """Render a lock-specific error panel with optional hint."""
    from src.compliance.console import print_error

    print_error(redact_secrets(message), hint=hint, title="Lock error", console=console)


def dumps_report_json(payload: dict[str, Any]) -> str:
    """Serialize a lock report payload for tests."""
    return json.dumps(payload, indent=2, sort_keys=True)


def collect_report_renderables(
    *,
    command: str,
    lockfile: dict[str, Any],
    pipeline_file: str,
    lock_file: str,
    matches: bool | None = None,
    verbose: bool = False,
) -> list[RenderableType]:
    """Return key renderables (used by tests without printing)."""
    inventory = lockfile.get("inventory") or {}
    health = _inventory_health(inventory)
    counts = summarize_inventory(inventory)
    items: list[RenderableType] = [
        _header_panel(
            title=command,
            outcome="Inventory locked",
            outcome_style="bold green",
            pipeline_file=pipeline_file,
            lock_file=lock_file,
            fingerprint=str(lockfile.get("fingerprint", "")),
        ),
        _counts_columns(counts, health),
        _health_banner(health),
    ]
    includes = _includes_table(inventory, verbose=verbose)
    if includes:
        items.append(includes)
    images = _images_table(inventory, verbose=verbose)
    if images:
        items.append(images)
    return items
