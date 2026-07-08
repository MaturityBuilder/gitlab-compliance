"""Render pipeline documentation as a Swagger-style HTML page."""

from __future__ import annotations

import html
from typing import Any

import src.modules.common as common


def _escape(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return html.escape(common.format_value(value))
    return html.escape(str(value))


def _render_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return '<p class="empty">No entries.</p>'

    head = "".join(f"<th>{_escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{_escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table class=\"data-table\"><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def _render_rules_table(rules: list[dict]) -> str:
    if not rules:
        return ""

    headers, rows = common.dict_list_rows(rules)
    if not headers:
        return ""
    return (
        '<div class="subsection"><h4>Rules</h4>'
        + _render_table(headers, rows)
        + "</div>"
    )


def _render_job_block(job: dict) -> str:
    job_id = html.escape(job["name"].replace(" ", "-"))
    method_class = "template" if job["is_template"] else "job"
    method_label = "TEMPLATE" if job["is_template"] else "JOB"

    attribute_rows = [
        [item["key"], common.format_value(item["value"])] for item in job["attributes"]
    ]
    nested_rows = [
        [item["attribute"], item["key"], common.format_value(item["value"])]
        for item in job["nested"]
    ]

    attributes_html = (
        _render_table(["Attribute", "Value"], attribute_rows) if attribute_rows else ""
    )
    nested_html = (
        _render_table(["Attribute", "Key", "Value"], nested_rows) if nested_rows else ""
    )
    rules_html = _render_rules_table(job["rules"])

    return f"""
    <article class="opblock opblock-{method_class}" data-name="{_escape(job['display_name'])}" id="job-{job_id}">
      <button class="opblock-summary" type="button" aria-expanded="false">
        <span class="opblock-summary-method">{method_label}</span>
        <span class="opblock-summary-path">{_escape(job['display_name'])}</span>
      </button>
      <div class="opblock-body hidden">
        {attributes_html}
        {rules_html}
        {('<div class="subsection"><h4>Nested Attributes</h4>' + nested_html + '</div>') if nested_html else ''}
      </div>
    </article>
    """


def _jobs_grouped(data: dict) -> list[dict]:
    """Return grouped jobs, falling back to a flat list when unfiltered."""
    grouped = data.get("jobs_grouped")
    if grouped is not None:
        return grouped
    jobs = data.get("jobs", [])
    return [{"group_key": "", "jobs": jobs}]


def _is_section_excluded(data: dict, section: str) -> bool:
    return section in data.get("exclude_sections", set())


def _render_sidebar_nav(data: dict) -> str:
    links = [("overview", "Overview")]
    if not _is_section_excluded(data, "inputs"):
        links.append(("inputs", "Inputs", len(data["inputs"])))
    if not _is_section_excluded(data, "variables"):
        links.append(("variables", "Variables", len(data["variables"])))
    if not _is_section_excluded(data, "includes"):
        links.append(("includes", "Includes", len(data["includes"])))
    if data["workflow_rules"] and not _is_section_excluded(data, "workflow"):
        links.append(("workflow", "Workflow", len(data["workflow_rules"])))
    if not _is_section_excluded(data, "jobs"):
        links.append(("jobs", "Jobs", len(data["jobs"])))

    items = []
    for entry in links:
        section_id = entry[0]
        label = entry[1]
        count = entry[2] if len(entry) > 2 else None
        count_html = (
            f'<span class="nav-count">{count}</span>' if count is not None else ""
        )
        items.append(
            f'<a class="nav-link" href="#{section_id}">{_escape(label)}{count_html}</a>'
        )

    if not _is_section_excluded(data, "jobs"):
        group_by = data.get("group_by")
        for block in _jobs_grouped(data):
            group_key = block.get("group_key", "")
            if group_by and group_key:
                items.append(
                    f'<span class="nav-link nav-link-child nav-group">{_escape(group_by.title())} · {_escape(group_key)}</span>'
                )
            for job in block.get("jobs", []):
                items.append(
                    f'<a class="nav-link nav-link-child" href="#job-{_escape(job["name"].replace(" ", "-"))}">{_escape(job["display_name"])}</a>'
                )
    return f'<nav class="sidebar">{"".join(items)}</nav>'


def _render_jobs_html(data: dict) -> str:
    parts: list[str] = []
    group_by = data.get("group_by")
    for block in _jobs_grouped(data):
        group_key = block.get("group_key", "")
        if group_by and group_key:
            parts.append(
                f'<h3 class="job-group-heading">{_escape(group_by.title())} · {_escape(group_key)}</h3>'
            )
        for job in block.get("jobs", []):
            parts.append(_render_job_block(job))
    return "".join(parts)


def render_swagger_html(data: dict) -> str:
    input_rows = [
        [
            item["key"],
            item["value"],
            item["description"],
            item["options"],
            item["expand"],
        ]
        for item in data["inputs"]
    ]
    variable_rows = [
        [
            item["key"],
            item["value"],
            item["description"],
            item["options"],
            item["expand"],
        ]
        for item in data["variables"]
    ]
    include_rows = [
        [
            item["include_type"],
            item["project"],
            item["version"],
            "valid" if item["valid_version"] else "invalid",
            item["file"],
            common.format_dict_summary(item["variables"]),
            common.format_rules_summary(item["rules"]),
        ]
        for item in data["includes"]
    ]

    jobs_html = (
        _render_jobs_html(data) if not _is_section_excluded(data, "jobs") else ""
    )
    workflow_html = (
        _render_rules_table(data["workflow_rules"])
        if data["workflow_rules"] and not _is_section_excluded(data, "workflow")
        else ""
    )

    overview_bits = []
    if not _is_section_excluded(data, "jobs"):
        overview_bits.append(f"<strong>{len(data['jobs'])}</strong> jobs")
    if not _is_section_excluded(data, "includes"):
        overview_bits.append(f"<strong>{len(data['includes'])}</strong> includes")
    if not _is_section_excluded(data, "variables"):
        overview_bits.append(f"<strong>{len(data['variables'])}</strong> variables")
    if not _is_section_excluded(data, "inputs"):
        overview_bits.append(f"<strong>{len(data['inputs'])}</strong> inputs")
    overview_summary = ", ".join(overview_bits) + "."

    inputs_section = ""
    if not _is_section_excluded(data, "inputs"):
        inputs_section = f"""
      <section class="section" id="inputs">
        <h2>Inputs</h2>
        {_render_table(["Key", "Value", "Description", "Options", "Expand"], input_rows)}
      </section>"""

    variables_section = ""
    if not _is_section_excluded(data, "variables"):
        variables_section = f"""
      <section class="section" id="variables">
        <h2>Variables</h2>
        {_render_table(["Key", "Value", "Description", "Options", "Expand"], variable_rows)}
      </section>"""

    includes_section = ""
    if not _is_section_excluded(data, "includes"):
        includes_section = f"""
      <section class="section" id="includes">
        <h2>Includes</h2>
        {_render_table(["Include Type", "Project", "Version", "Valid Version", "File", "Variables", "Rules"], include_rows)}
      </section>"""

    workflow_section = ""
    if workflow_html:
        workflow_section = f"<section class='section' id='workflow'><h2>Workflow</h2>{workflow_html}</section>"

    jobs_section = ""
    if not _is_section_excluded(data, "jobs"):
        jobs_section = f"""
      <section class="section" id="jobs">
        <h2>Jobs</h2>
        {jobs_html if jobs_html else '<p class="empty">No jobs found.</p>'}
      </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitLab Docs - {_escape(data['config_file'])}</title>
  <style>
    :root {{
      --swagger-green: #49cc90;
      --swagger-blue: #61affe;
      --swagger-purple: #9012fe;
      --swagger-gray: #6b7c93;
      --swagger-dark: #3b4151;
      --swagger-bg: #fafafa;
      --swagger-border: #e8e8e8;
      --swagger-code: #41444e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: var(--swagger-dark);
      background: var(--swagger-bg);
    }}
    .topbar {{
      background: var(--swagger-dark);
      color: #fff;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    .topbar h1 {{
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }}
    .topbar .config-file {{
      opacity: 0.85;
      font-family: monospace;
      font-size: 0.95rem;
    }}
    .topbar .search {{
      margin-left: auto;
      min-width: 240px;
      padding: 8px 12px;
      border: none;
      border-radius: 4px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 260px 1fr;
      min-height: calc(100vh - 56px);
    }}
    .sidebar {{
      background: #fff;
      border-right: 1px solid var(--swagger-border);
      padding: 16px 0;
      position: sticky;
      top: 56px;
      height: calc(100vh - 56px);
      overflow-y: auto;
    }}
    .nav-link {{
      display: flex;
      justify-content: space-between;
      padding: 8px 20px;
      color: var(--swagger-dark);
      text-decoration: none;
      font-size: 0.95rem;
    }}
    .nav-link:hover, .nav-link:focus {{
      background: #f0f3f8;
    }}
    .nav-link-child {{
      padding-left: 32px;
      font-family: monospace;
      font-size: 0.85rem;
    }}
    .nav-count {{
      background: #e8eef7;
      border-radius: 999px;
      padding: 0 8px;
      font-size: 0.75rem;
    }}
    .content {{
      padding: 24px 32px 48px;
      max-width: 1100px;
    }}
    .section {{
      margin-bottom: 32px;
    }}
    .section h2 {{
      margin: 0 0 16px;
      font-size: 1.5rem;
      border-bottom: 1px solid var(--swagger-border);
      padding-bottom: 8px;
    }}
    .section p {{
      color: #555;
      line-height: 1.5;
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      background: #fff;
      border: 1px solid var(--swagger-border);
      margin-bottom: 16px;
    }}
    .data-table th, .data-table td {{
      border: 1px solid var(--swagger-border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .data-table th {{
      background: #f7f7f7;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .empty {{
      color: #777;
      font-style: italic;
    }}
    .opblock {{
      margin-bottom: 12px;
      border: 1px solid var(--swagger-border);
      border-radius: 4px;
      background: #fff;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}
    .opblock-summary {{
      width: 100%;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      border: none;
      background: transparent;
      cursor: pointer;
      text-align: left;
    }}
    .opblock-summary-method {{
      min-width: 88px;
      text-align: center;
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      border-radius: 3px;
      padding: 6px 10px;
    }}
    .opblock-job .opblock-summary-method {{ background: var(--swagger-blue); }}
    .opblock-template .opblock-summary-method {{ background: var(--swagger-gray); }}
    .opblock-summary-path {{
      font-family: monospace;
      font-size: 1rem;
      font-weight: 600;
    }}
    .opblock-body {{
      padding: 0 16px 16px;
      border-top: 1px solid var(--swagger-border);
    }}
    .opblock-body.hidden {{
      display: none;
    }}
    .subsection h4 {{
      margin: 16px 0 8px;
      font-size: 0.95rem;
      color: var(--swagger-code);
    }}
    .badge-valid {{ color: #1b7f4c; font-weight: 600; }}
    .badge-invalid {{ color: #c0392b; font-weight: 600; }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; height: auto; border-right: none; border-bottom: 1px solid var(--swagger-border); }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <h1>GitLab Docs</h1>
    <span class="config-file">{_escape(data['config_file'])}</span>
    <input class="search" id="search" type="search" placeholder="Filter jobs and sections">
  </header>
  <div class="layout">
    {_render_sidebar_nav(data)}
    <main class="content">
      <section class="section" id="overview">
        <h2>Overview</h2>
        <p>Swagger-style documentation generated from <code>{_escape(data['config_file'])}</code>.</p>
        <p>{overview_summary}</p>
      </section>

      {inputs_section}

      {variables_section}

      {includes_section}

      {workflow_section}

      {jobs_section}
    </main>
  </div>
  <script>
    const searchInput = document.getElementById("search");
    const blocks = Array.from(document.querySelectorAll(".opblock"));
    const sections = Array.from(document.querySelectorAll(".section"));

    document.querySelectorAll(".opblock-summary").forEach((button) => {{
      button.addEventListener("click", () => {{
        const body = button.nextElementSibling;
        const expanded = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", expanded ? "false" : "true");
        body.classList.toggle("hidden", expanded);
      }});
    }});

    searchInput.addEventListener("input", () => {{
      const query = searchInput.value.trim().toLowerCase();
      blocks.forEach((block) => {{
        const name = (block.dataset.name || "").toLowerCase();
        block.style.display = !query || name.includes(query) ? "" : "none";
      }});
      sections.forEach((section) => {{
        if (section.id === "jobs") {{
          return;
        }}
        const text = section.textContent.toLowerCase();
        section.style.display = !query || text.includes(query) ? "" : "none";
      }});
    }});
  </script>
</body>
</html>
"""
