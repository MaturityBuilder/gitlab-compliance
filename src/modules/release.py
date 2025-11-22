# #!/usr/bin/env python3
# import click
# import gitlab
# from datetime import datetime
# from rich.console import Console
# from rich.table import Table
# from dateutil import parser as dateparser
# from pathlib import Path
# import sys


# console = Console()

# def summarize_file(
#     body,
#     model_name: str = "facebook/bart-large-cnn",
#     max_length: int = 373,
#     min_length: int = 100
# ) -> str:
#     """
#     Summarize the contents of a text file using a transformer model.

#     Args:
#         body: text to summarize.
#         model_name: Hugging Face model ID for summarization.
#         max_length: Maximum length of the summary.
#         min_length: Minimum length of the summary.

#     Returns:
#         str: A short summary of the file content.
#     """
#     # Load summarization model
#     # summarizer = pipeline("text-generation", model=model_name, truncation=True)


#     with open("changelog.md", "r", encoding="utf-8") as f:
#         text = f.read()[:900]  #
#     from copilot_api import Copilot

#     # Initialize Copilot
#     copilot = Copilot()

#     # Basic chat example
#     messages = [
#         {"role": "system", "content": text}
#     ]

#     # Stream responses
#     for response in copilot.create_completion(
#         model="Copilot",
#         messages=messages,
#         stream=True
#     ):
#         if isinstance(response, str):
#             print(response, end='', flush=True)
#     # console.print(len(text))
#     # exit(1)
#     # Some models have input length limits, so we handle long text
#     if len(text) > 4000:
#         text = text[:4000]  # truncate to keep inference fast
#     text=f"{text}"
#     # Generate summary
#     result = summarizer(text, max_length=max_length, min_length=min_length)
#     summary = result
#     return summary

# def get_commits_since_last_tag(gl, project_id):
#     """Fetch commits since last tag for a GitLab project."""
#     project = gl.projects.get(project_id)
#     tags = project.tags.list(get_all=True)

#     if not tags:
#         last_tag_date = datetime.fromtimestamp(0)  # Unix epoch if no tag exists
#         tag_name = "No previous tag"
#     else:
#         last_tag = tags[0]
#         tag_name = last_tag.name
#         committed_date = last_tag.commit["committed_date"]
#         try:
#             last_tag_date = dateparser.parse(committed_date)
#         except Exception as e:
#             console.print(f"[red]Warning:[/red] could not parse tag date '{committed_date}': {e}")
#             last_tag_date = datetime.fromtimestamp(0)

#     commits = project.commits.list(
#         since=last_tag_date.isoformat(),
#         all=True,
#         order_by="created_at",
#         sort="desc"
#     )

#     return tag_name, commits


# def summarize_commits(commits):
#     """Group commits by type prefix (e.g., feat:, fix:, chore:)"""
#     summary = {"feat": 0, "fix": 0, "chore": 0, "other": 0}
#     for c in commits:
#         msg = c.title.lower()
#         if msg.startswith("feat"):
#             summary["feat"] += 1
#         elif msg.startswith("fix"):
#             summary["fix"] += 1
#         elif msg.startswith("chore"):
#             summary["chore"] += 1
#         else:
#             summary["other"] += 1
#     return summary


# def generate_markdown(project_id, tag_name, commits, summary, output_dir):
#     """Generate markdown release notes for a single project."""
#     project_slug = project_id.replace("/", "_")
#     timestamp = datetime.now().strftime("%Y-%m-%d")
#     filename = Path(output_dir) / f"release_notes_{project_slug}_{timestamp}.md"

#     lines = []
#     lines.append(f"# Release Notes for {project_id}")
#     lines.append(f"**Date:** {timestamp}")
#     lines.append(f"**Since tag:** {tag_name}")
#     lines.append("")
#     lines.append("## Summary")
#     lines.append("")
#     lines.append(f"- Features: {summary['feat']}")
#     lines.append(f"- Fixes: {summary['fix']}")
#     lines.append(f"- Chores: {summary['chore']}")
#     lines.append(f"- Other: {summary['other']}")
#     lines.append(f"- Total commits: {len(commits)}")
#     lines.append("")
#     lines.append("## Commits")
#     lines.append("")

#     for c in commits:
#         lines.append(f"- {c.title} ({c.short_id})")

#     filename.write_text("\n".join(lines), encoding="utf-8")
#     console.print(f"[green]✅ Markdown written:[/green] {filename}")
#     return filename



# @click.command()
# @click.option("--token", envvar="GITLAB_TOKEN", required=True, help="GitLab personal access token")
# @click.option("--url", envvar="GITLAB_URL", default="https://gitlab.com", show_default=True, help="GitLab instance URL")
# @click.option("--projects", required=True, multiple=True, help="List of GitLab project IDs or full paths")
# @click.option("--markdown", "markdown_dir", default=".", type=click.Path(file_okay=False, path_type=Path), help="Directory to output Markdown release notes")
# def release_notes(token, url, projects, markdown_dir):
#     """
#     Generate release notes for multiple GitLab projects based on commits since the last tag.
#     Optionally outputs Markdown files.
#     """
#     gl = gitlab.Gitlab(url, private_token=token)
#     all_summaries = []
#     markdown_dir="./"
#     # if markdown_dir:
#     #     console.print(f"[cyan]Markdown output enabled in:[/cyan] {markdown_dir}\n")

#     for project_id in projects:
#         console.rule(f"[bold blue]Processing project: {project_id}")
#         try:
#             tag_name, commits = get_commits_since_last_tag(gl, project_id)

#             console.print(f"Last tag: [green]{tag_name}[/green]")
#             console.print(f"Found [yellow]{len(commits)}[/yellow] commits since last tag.\n")

#             summary = summarize_commits(commits)
#             all_summaries.append((project_id, summary, commits))

#             console.print("[bold underline]Release Notes Preview:[/bold underline]")
#             for c in commits[:10]:
#                 console.print(f"- {c.title} ({c.short_id})")
#             console.print("\n")

#             if markdown_dir:
#                 generate_markdown(project_id, tag_name, commits, summary, markdown_dir)

#         except Exception as e:
#             console.print(f"[red]Error processing {project_id}: {e}[/red]", file=sys.stderr)

#     console.rule("[bold green]Summary across all projects")
#     table = Table(show_header=True, header_style="bold magenta")
#     table.add_column("Project")
#     table.add_column("Features")
#     table.add_column("Fixes")
#     table.add_column("Chores")
#     table.add_column("Other")
#     table.add_column("Total")
#     overview=summarize_file(str(commits))
#     for project_id, summary, commits in all_summaries:
#         total = len(commits)
#         table.add_row(
#             project_id,
#             str(summary["feat"]),
#             str(summary["fix"]),
#             str(summary["chore"]),
#             str(summary["other"]),
#             str(total)
#         )
#     console.print(f"[bold blue]{overview}")
#     console.print(table)

