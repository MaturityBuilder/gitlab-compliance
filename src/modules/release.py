#!/usr/bin/env python3
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import click
import gitlab
import semver
from rich.console import Console
from rich.table import Table

console = Console()

COMMIT_TYPE_RE = re.compile(
    r"^(feat|fix|chore|docs|refactor|perf|ci|build)(\([^)]+\))?!?:",
    re.IGNORECASE,
)

SUMMARY_BUCKETS = ("feat", "fix", "chore", "other")
BUCKET_LABELS = {
    "feat": "Features",
    "fix": "Fixes",
    "chore": "Chores",
    "other": "Other",
}

PREVIEW_LIMIT = 10


def parse_gitlab_date(value: str) -> datetime:
    """Parse an ISO-8601 timestamp from the GitLab API."""
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def classify_commit(title: str) -> str:
    """Classify a commit title into feat, fix, chore, or other."""
    match = COMMIT_TYPE_RE.match(title.strip())
    if not match:
        return "other"
    commit_type = match.group(1).lower()
    if commit_type in ("feat", "fix", "chore"):
        return commit_type
    return "other"


def summarize_commits(commits) -> dict[str, int]:
    """Count commits by conventional-commit bucket."""
    summary = {bucket: 0 for bucket in SUMMARY_BUCKETS}
    for commit in commits:
        summary[classify_commit(commit.title)] += 1
    return summary


def _tag_committed_date(tag) -> datetime:
    committed_date = tag.commit["committed_date"]
    try:
        return parse_gitlab_date(committed_date)
    except ValueError as exc:
        console.print(
            f"[red]Warning:[/red] could not parse tag date '{committed_date}': {exc}"
        )
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _semver_sort_key(tag_name: str) -> tuple[int, semver.Version | None]:
    cleaned = tag_name.lstrip("vV")
    if semver.Version.is_valid(cleaned):
        return (1, semver.Version.parse(cleaned))
    return (0, None)


def sort_tags(tags: list) -> list:
    """Sort tags by semver when possible, otherwise by commit date descending."""
    semver_tags = [tag for tag in tags if _semver_sort_key(tag.name)[1] is not None]
    if semver_tags:
        return sorted(
            semver_tags,
            key=lambda tag: _semver_sort_key(tag.name)[1],
            reverse=True,
        )

    return sorted(tags, key=lambda tag: _tag_committed_date(tag), reverse=True)


def resolve_baseline_tag(tags: list, since_tag: str | None = None) -> tuple[str, datetime, str | None]:
    """Return baseline tag name, date, and commit SHA."""
    if since_tag:
        for tag in tags:
            if tag.name == since_tag:
                return tag.name, _tag_committed_date(tag), tag.commit["id"]
        raise ValueError(f"Tag '{since_tag}' not found")

    if not tags:
        return "No previous tag", datetime.fromtimestamp(0, tz=timezone.utc), None

    ordered = sort_tags(tags)
    baseline = ordered[0]
    return baseline.name, _tag_committed_date(baseline), baseline.commit["id"]


def filter_commits_since_tag(commits, tag_sha: str | None) -> list:
    """Drop the baseline tag commit from the result set when present."""
    if not tag_sha:
        return list(commits)
    return [commit for commit in commits if commit.id != tag_sha]


def get_commits_since_last_tag(gl, project_id: str, since_tag: str | None = None):
    """Fetch commits since the baseline tag for a GitLab project."""
    project = gl.projects.get(project_id)
    tags = project.tags.list(get_all=True, order_by="version", sort="desc")
    tag_name, last_tag_date, tag_sha = resolve_baseline_tag(tags, since_tag=since_tag)

    commits = project.commits.list(
        since=last_tag_date.isoformat(),
        all=True,
        order_by="created_at",
        sort="desc",
    )
    filtered = filter_commits_since_tag(commits, tag_sha)
    return project, tag_name, last_tag_date, filtered


def _format_tag_date(tag_date: datetime) -> str:
    if tag_date.timestamp() == 0:
        return "n/a"
    return tag_date.strftime("%Y-%m-%d")


def _commit_line(commit) -> str:
    author = getattr(commit, "author_name", None)
    author_suffix = f" — {author}" if author else ""
    web_url = getattr(commit, "web_url", None)
    if web_url:
        return f"- [{commit.title}]({web_url}) (`{commit.short_id}`){author_suffix}"
    return f"- {commit.title} (`{commit.short_id}`){author_suffix}"


def build_markdown(
    project_id: str,
    tag_name: str,
    tag_date: datetime,
    commits,
    summary: dict[str, int],
    project_web_url: str | None = None,
) -> str:
    """Build grouped markdown release notes for a single project."""
    generated = datetime.now().strftime("%Y-%m-%d")
    lines = [f"# Release Notes — {project_id}"]
    if project_web_url:
        lines.append(f"**Project:** [{project_id}]({project_web_url})")
    lines.append(f"**Generated:** {generated}")
    lines.append(f"**Since tag:** {tag_name} ({_format_tag_date(tag_date)})")
    lines.append(f"**Commits:** {len(commits)}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        " | ".join(
            f"{BUCKET_LABELS[bucket]}: {summary[bucket]}" for bucket in SUMMARY_BUCKETS
        )
    )
    lines.append("")

    grouped: dict[str, list] = defaultdict(list)
    for commit in commits:
        grouped[classify_commit(commit.title)].append(commit)

    for bucket in SUMMARY_BUCKETS:
        bucket_commits = grouped[bucket]
        if not bucket_commits:
            continue
        lines.append(f"## {BUCKET_LABELS[bucket]}")
        lines.append("")
        for commit in bucket_commits:
            lines.append(_commit_line(commit))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _sanitize_filename_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def generate_markdown(
    project_id: str,
    tag_name: str,
    tag_date: datetime,
    commits,
    summary: dict[str, int],
    output_dir: Path,
    project_web_url: str | None = None,
) -> Path:
    """Write markdown release notes for a single project."""
    output_dir.mkdir(parents=True, exist_ok=True)
    project_slug = _sanitize_filename_part(project_id.replace("/", "_"))
    tag_slug = _sanitize_filename_part(tag_name)
    filename = output_dir / f"release_notes_{project_slug}_since_{tag_slug}.md"
    filename.write_text(
        build_markdown(
            project_id,
            tag_name,
            tag_date,
            commits,
            summary,
            project_web_url=project_web_url,
        ),
        encoding="utf-8",
    )
    console.print(f"[green]Markdown written:[/green] {filename}")
    return filename


def render_summary_table(all_summaries: list[tuple[str, dict[str, int], list]]) -> Table:
    """Build a Rich table summarizing all processed projects."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project")
    table.add_column("Features")
    table.add_column("Fixes")
    table.add_column("Chores")
    table.add_column("Other")
    table.add_column("Total")

    for project_id, summary, commits in all_summaries:
        table.add_row(
            project_id,
            str(summary["feat"]),
            str(summary["fix"]),
            str(summary["chore"]),
            str(summary["other"]),
            str(len(commits)),
        )
    return table


def print_release_preview(commits) -> None:
    """Print a short console preview of commits."""
    if not commits:
        console.print("[yellow]No commits since the baseline tag.[/yellow]\n")
        return

    console.print("[bold underline]Release Notes Preview:[/bold underline]")
    for commit in commits[:PREVIEW_LIMIT]:
        console.print(f"- {commit.title} (`{commit.short_id}`)")
    remaining = len(commits) - PREVIEW_LIMIT
    if remaining > 0:
        console.print(f"... and {remaining} more commits")
    console.print("")


@click.command()
@click.option("--token", envvar="GITLAB_TOKEN", required=True, help="GitLab personal access token")
@click.option("--url", envvar="GITLAB_URL", default="https://gitlab.com", show_default=True, help="GitLab instance URL")
@click.option("--projects", required=True, multiple=True, help="List of GitLab project IDs or full paths")
@click.option(
    "--since-tag",
    default=None,
    help="Baseline tag name (default: latest semver tag, else most recent by date)",
)
@click.option(
    "--markdown",
    "markdown_dir",
    default=".",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to output Markdown release notes",
)
@click.option("--no-write", is_flag=True, help="Skip writing Markdown files")
def release_notes(token, url, projects, since_tag, markdown_dir, no_write):
    """
    Generate release notes for multiple GitLab projects based on commits since the last tag.
    Optionally outputs Markdown files.
    """
    gl = gitlab.Gitlab(url, private_token=token)
    gl.auth()

    all_summaries: list[tuple[str, dict[str, int], list]] = []
    failures = 0

    for project_id in projects:
        console.rule(f"[bold blue]Processing project: {project_id}")
        try:
            project, tag_name, tag_date, commits = get_commits_since_last_tag(
                gl, project_id, since_tag=since_tag
            )

            console.print(f"Last tag: [green]{tag_name}[/green] ({_format_tag_date(tag_date)})")
            console.print(f"Found [yellow]{len(commits)}[/yellow] commits since last tag.\n")

            summary = summarize_commits(commits)
            all_summaries.append((project_id, summary, commits))
            print_release_preview(commits)

            if not no_write:
                generate_markdown(
                    project_id,
                    tag_name,
                    tag_date,
                    commits,
                    summary,
                    markdown_dir,
                    project_web_url=getattr(project, "web_url", None),
                )

        except Exception as exc:
            failures += 1
            console.print(f"[red]Error processing {project_id}: {exc}[/red]")

    if not all_summaries:
        console.print("[yellow]No projects processed successfully.[/yellow]")
        raise SystemExit(1 if failures else 0)

    console.rule("[bold green]Summary across all projects")
    console.print(render_summary_table(all_summaries))

    if failures:
        raise SystemExit(1)
