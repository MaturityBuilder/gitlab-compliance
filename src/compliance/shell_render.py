"""Shell-check report renderers for markdown and HTML output."""

from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from src.compliance.builtin_policies import BUILTIN_SHELL_POLICIES_DIR
from src.compliance.include_resolution import REASON_MESSAGES
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.secret_redact import redact_secrets
from src.modules.common import render_markdown_table

JOB_VIOLATION_RE = re.compile(
    r"Job '([^']+)'\s+(.+):(\d+):\s*(.+?)(?:\s+via:\s+(.+))?$"
)
JOB_BOUNDARY_RE = re.compile(r"; (?=Job ')")


@dataclass(frozen=True)
class ShellViolation:
    job: str
    location: str
    message: str
    inheritance: str = ""


def split_location(location: str) -> tuple[str, int]:
    """Split ``path:line`` supporting Windows drive letters."""
    if not location:
        return "", 0
    if ":" not in location:
        return location, 0
    file_part, line_part = location.rsplit(":", 1)
    if line_part.isdigit():
        return file_part, int(line_part)
    return location, 0


def escape_markdown_cell(text: str) -> str:
    """Escape pipe characters so markdown table cells stay intact."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def _relative_path(path: str, base_dir: str | None = None) -> str:
    normalized = path.replace("\\", "/")
    if base_dir:
        try:
            return os.path.relpath(normalized, base_dir).replace("\\", "/")
        except ValueError:
            pass
    return normalized.lstrip("./")


def _display_location(location: str, pipeline_file: str) -> str:
    if not location:
        return ""
    file_part, line_number = split_location(location)
    pipeline_dir = os.path.dirname(os.path.abspath(pipeline_file)) or "."
    if os.path.isabs(file_part) or (len(file_part) > 1 and file_part[1] == ":"):
        rel_file = _relative_path(file_part, pipeline_dir)
        return f"{rel_file}:{line_number}" if line_number else rel_file
    return location


def _display_policies_dir(features_dir: str) -> str:
    if os.path.abspath(features_dir) == os.path.abspath(BUILTIN_SHELL_POLICIES_DIR):
        return "Packaged GLCI-BUILTIN-SHELL policies"
    return features_dir


def _coverage_gap_rows(unresolved_includes: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in unresolved_includes:
        include_type = str(item.get("include_type", ""))
        reference = str(item.get("reference", ""))
        reason = REASON_MESSAGES.get(
            str(item.get("reason", "")), str(item.get("reason", ""))
        )
        detail = str(item.get("detail", ""))
        if detail:
            reason = f"{reason} ({detail})"
        location = ""
        source_file = str(item.get("source_file", ""))
        line = int(item.get("line") or 0)
        if source_file:
            location = source_file
            if line:
                location = f"{location}:{line}"
        rows.append([include_type, reference, reason, location or "—"])
    return rows


def _render_coverage_gaps_markdown(unresolved_includes: list[dict]) -> list[str]:
    if not unresolved_includes:
        return []
    return [
        f"## Coverage gaps ({len(unresolved_includes)})",
        "",
        (
            "> Scripts from these include entries were not validated. "
            "Use `--token` and `--resolve-external-includes` for project and "
            "remote includes."
        ),
        "",
        render_markdown_table(
            ["Type", "Reference", "Reason", "Declared in"],
            _coverage_gap_rows(unresolved_includes),
        ),
        "",
    ]


def _render_coverage_gaps_html(unresolved_includes: list[dict]) -> str:
    if not unresolved_includes:
        return ""
    rows = []
    for row in _coverage_gap_rows(unresolved_includes):
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(row[0])}</code></td>"
            f"<td>{html.escape(row[1])}</td>"
            f"<td>{html.escape(row[2])}</td>"
            f"<td><code>{html.escape(row[3])}</code></td>"
            "</tr>"
        )
    return (
        f"<h2>Coverage gaps ({len(unresolved_includes)})</h2>"
        "<p class='note'>Scripts from these include entries were not validated. "
        "Use <code>--token</code> and <code>--resolve-external-includes</code> "
        "for project and remote includes.</p>"
        "<table class='findings'>"
        "<thead><tr><th>Type</th><th>Reference</th><th>Reason</th>"
        "<th>Declared in</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def parse_shell_violations(message: str) -> list[ShellViolation]:
    """Parse ASSERT FAILED shell-check messages into structured violations."""
    text = redact_secrets(message or "").strip()
    if text.startswith("ASSERT FAILED: "):
        text = text[len("ASSERT FAILED: ") :]

    violations: list[ShellViolation] = []
    # Only split between job findings — messages may contain "; ".
    for part in JOB_BOUNDARY_RE.split(text):
        part = part.strip()
        if not part:
            continue
        match = JOB_VIOLATION_RE.match(part)
        if match:
            violations.append(
                ShellViolation(
                    job=match.group(1),
                    location=f"{match.group(2)}:{match.group(3)}",
                    message=match.group(4),
                    inheritance=match.group(5) or "",
                )
            )
        else:
            violations.append(ShellViolation(job="", location="", message=part))
    return violations


def _group_by_status(result: ComplianceResult) -> dict[str, list[ScenarioResult]]:
    grouped: dict[str, list[ScenarioResult]] = {
        "passed": [],
        "failed": [],
        "skipped": [],
    }
    for scenario in result.scenario_results:
        grouped.setdefault(scenario.status, []).append(scenario)
    return grouped


def _report_meta(pipeline_file: str, features_dir: str) -> tuple[str, str, str, str]:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    pipeline = _relative_path(pipeline_file)
    policies = _display_policies_dir(features_dir)
    return generated, pipeline, policies, pipeline_file


def _violation_rows(
    violations: list[ShellViolation], pipeline_file: str
) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in violations:
        rows.append(
            [
                f"`{escape_markdown_cell(item.job)}`" if item.job else "—",
                (
                    f"`{escape_markdown_cell(_display_location(item.location, pipeline_file))}`"
                    if item.location
                    else "—"
                ),
                escape_markdown_cell(item.message),
                escape_markdown_cell(item.inheritance) if item.inheritance else "—",
            ]
        )
    return rows


def render_shell_check_markdown(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    *,
    failures_only: bool = False,
) -> str:
    """Render a shell-check markdown report with structured findings."""
    grouped = _group_by_status(result)
    generated, pipeline, policies, _ = _report_meta(pipeline_file, features_dir)
    overall = "PASS" if result.success else "FAIL"

    lines = [
        "# Shell Check Report",
        "",
        (
            "> Validates `before_script`, `script`, and `after_script` using "
            "packaged GLCI-BUILTIN-SHELL policies. This is **not** the external "
            "ShellCheck binary."
        ),
        "",
        f"- **Pipeline:** `{pipeline}`",
        f"- **Policies:** {policies}",
        f"- **Generated:** {generated}",
        "",
    ]

    coverage_section = _render_coverage_gaps_markdown(result.unresolved_includes)
    if coverage_section:
        lines.extend(coverage_section)

    lines.extend(
        [
            "## Summary",
            "",
            render_markdown_table(
                ["Status", "Count"],
                [
                    ["Passed", str(result.passed)],
                    ["Failed", str(result.failed)],
                    ["Skipped", str(result.skipped)],
                    ["Overall", overall],
                ],
            ),
            "",
        ]
    )

    if grouped["failed"]:
        lines.extend(
            [
                f"## Findings ({len(grouped['failed'])})",
                "",
            ]
        )
        for scenario in grouped["failed"]:
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            lines.extend(
                [
                    f"### {label} — {title}",
                    "",
                ]
            )
            if scenario.description:
                lines.append(f"{scenario.description}")
                lines.append("")
            if scenario.owasp_cicd:
                lines.append(f"- **OWASP CI/CD:** {scenario.owasp_cicd}")
            if scenario.iso27001:
                lines.append(f"- **ISO 27001:** {scenario.iso27001}")
            if scenario.owasp_cicd or scenario.iso27001:
                lines.append("")

            violations = parse_shell_violations(scenario.message)
            if violations and any(v.job or v.location for v in violations):
                lines.append(
                    render_markdown_table(
                        ["Job", "Location", "Issue", "Inheritance"],
                        _violation_rows(violations, pipeline_file),
                    )
                )
            elif scenario.message:
                lines.append(f"- **Details:** {redact_secrets(scenario.message)}")
            lines.append("")

    if not failures_only and grouped["skipped"]:
        lines.extend(
            [
                f"## Skipped policies ({len(grouped['skipped'])})",
                "",
            ]
        )
        for scenario in grouped["skipped"]:
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            reason = redact_secrets(
                scenario.message or "Filter did not match any entities."
            )
            lines.append(f"- `{label}` — {title}: {reason}")
        lines.append("")

    if not failures_only and grouped["passed"]:
        lines.extend(
            [
                f"## Passed policies ({len(grouped['passed'])})",
                "",
                render_markdown_table(
                    ["Policy ID", "Title", "OWASP CI/CD", "ISO 27001"],
                    [
                        [
                            scenario.policy_id or scenario.feature,
                            scenario.title or scenario.name,
                            scenario.owasp_cicd or "",
                            scenario.iso27001 or "",
                        ]
                        for scenario in grouped["passed"]
                    ],
                ),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _render_violation_table_html(
    violations: list[ShellViolation], pipeline_file: str
) -> str:
    if not violations:
        return ""
    rows = []
    for item in violations:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(item.job or '—')}</code></td>"
            f"<td><code>{html.escape(_display_location(item.location, pipeline_file) or '—')}</code></td>"
            f"<td>{html.escape(item.message)}</td>"
            f"<td>{html.escape(item.inheritance or '—')}</td>"
            "</tr>"
        )
    return (
        "<table class='findings'>"
        "<thead><tr><th>Job</th><th>Location</th><th>Issue</th>"
        "<th>Inheritance</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _render_policy_section_html(
    scenarios: list[ScenarioResult],
    pipeline_file: str,
    *,
    status: str,
) -> str:
    if not scenarios:
        return ""
    blocks = []
    for scenario in scenarios:
        label = html.escape(scenario.policy_id or scenario.feature)
        title = html.escape(scenario.title or scenario.name)
        body = ""
        if status == "failed":
            violations = parse_shell_violations(scenario.message)
            if violations and any(v.job or v.location for v in violations):
                body = _render_violation_table_html(violations, pipeline_file)
            elif scenario.message:
                body = f"<pre>{html.escape(redact_secrets(scenario.message))}</pre>"
        elif status == "skipped":
            reason = redact_secrets(
                scenario.message or "Filter did not match any entities."
            )
            body = f"<p>{html.escape(reason)}</p>"
        description = ""
        if scenario.description:
            description = (
                f"<p class='policy-desc'>{html.escape(scenario.description)}</p>"
            )
        framework = ""
        if scenario.owasp_cicd:
            framework += (
                f"<p><strong>OWASP CI/CD:</strong> "
                f"{html.escape(scenario.owasp_cicd)}</p>"
            )
        if scenario.iso27001:
            framework += (
                f"<p><strong>ISO 27001:</strong> "
                f"{html.escape(scenario.iso27001)}</p>"
            )
        blocks.append(
            "<section class='policy'>"
            f"<h3><code>{label}</code> — {title}</h3>"
            f"{description}{framework}{body}"
            "</section>"
        )
    return "".join(blocks)


def render_shell_check_html(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    *,
    failures_only: bool = False,
) -> str:
    """Render a shell-check HTML report with structured findings."""
    grouped = _group_by_status(result)
    generated, pipeline, policies, _ = _report_meta(pipeline_file, features_dir)
    overall_class = "pass" if result.success else "fail"
    overall_label = "Shell Check Passed" if result.success else "Shell Check Failed"

    failed_html = _render_policy_section_html(
        grouped["failed"], pipeline_file, status="failed"
    )
    skipped_html = (
        ""
        if failures_only
        else _render_policy_section_html(
            grouped["skipped"], pipeline_file, status="skipped"
        )
    )

    passed_rows = []
    if not failures_only:
        for scenario in grouped["passed"]:
            passed_rows.append(
                "<tr>"
                f"<td><code>{html.escape(scenario.policy_id or scenario.feature)}</code></td>"
                f"<td>{html.escape(scenario.title or scenario.name)}</td>"
                f"<td>{html.escape(scenario.owasp_cicd or '—')}</td>"
                f"<td>{html.escape(scenario.iso27001 or '—')}</td>"
                "</tr>"
            )
    passed_section = ""
    if passed_rows:
        passed_section = (
            f"<h2>Passed policies ({len(grouped['passed'])})</h2>"
            "<table class='summary'>"
            "<thead><tr><th>Policy ID</th><th>Title</th>"
            "<th>OWASP CI/CD</th><th>ISO 27001</th></tr></thead>"
            f"<tbody>{''.join(passed_rows)}</tbody></table>"
        )

    skipped_section = ""
    if skipped_html:
        skipped_section = (
            f"<h2>Skipped policies ({len(grouped['skipped'])})</h2>{skipped_html}"
        )

    findings_section = ""
    if failed_html:
        findings_section = f"<h2>Findings ({len(grouped['failed'])})</h2>{failed_html}"

    coverage_section = _render_coverage_gaps_html(result.unresolved_includes)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shell Check Report</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 2rem auto;
      max-width: 1100px;
      color: #1f2937;
      line-height: 1.5;
    }}
    .banner.pass {{ background: #def7ec; border: 1px solid #84e1bc; color: #03543f; }}
    .banner.fail {{ background: #fde8e8; border: 1px solid #f98080; color: #9b1c1c; }}
    .banner {{
      padding: 1rem 1.25rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
      font-weight: 600;
      font-size: 1.1rem;
    }}
    .note {{
      background: #f3f4f6;
      border-left: 4px solid #6b7280;
      padding: 0.75rem 1rem;
      margin-bottom: 1.5rem;
      color: #374151;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0 1.5rem;
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 0.65rem 0.75rem;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #f9fafb; }}
    .meta {{ color: #6b7280; margin-bottom: 1rem; }}
    .policy {{ margin-bottom: 1.75rem; }}
    .policy h3 {{ margin-bottom: 0.35rem; }}
    .policy-desc {{ color: #4b5563; margin-top: 0; }}
    pre {{
      white-space: pre-wrap;
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      padding: 0.75rem;
      margin: 0.5rem 0 0;
    }}
    table.findings td:nth-child(3) {{ min-width: 220px; }}
  </style>
</head>
<body>
  <div class="banner {overall_class}">{overall_label}</div>
  <p class="note">
    Validates <code>before_script</code>, <code>script</code>, and
    <code>after_script</code> using packaged GLCI-BUILTIN-SHELL policies.
    This is <strong>not</strong> the external ShellCheck binary.
  </p>
  <p class="meta">
    <strong>Pipeline:</strong> {html.escape(pipeline)}<br>
    <strong>Policies:</strong> {html.escape(policies)}<br>
    <strong>Generated:</strong> {generated}
  </p>

  <h2>Summary</h2>
  <table class="summary">
    <thead><tr><th>Status</th><th>Count</th></tr></thead>
    <tbody>
      <tr><td>Passed</td><td>{result.passed}</td></tr>
      <tr><td>Failed</td><td>{result.failed}</td></tr>
      <tr><td>Skipped</td><td>{result.skipped}</td></tr>
      <tr><td><strong>Overall</strong></td><td><strong>{'PASS' if result.success else 'FAIL'}</strong></td></tr>
    </tbody>
  </table>

  {coverage_section}
  {findings_section}
  {skipped_section}
  {passed_section}
</body>
</html>
"""


def render_shell_check_mr_comment(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    *,
    failures_only: bool = False,
) -> str:
    """Render a compact shell-check merge-request comment."""
    grouped = _group_by_status(result)
    _, pipeline, policies, _ = _report_meta(pipeline_file, features_dir)
    overall = (
        ":white_check_mark: **Shell check passed**"
        if result.success
        else ":x: **Shell check failed**"
    )
    lines = [
        "### Shell Check Report",
        "",
        overall,
        "",
        (
            "> Validates CI scripts with packaged GLCI-BUILTIN-SHELL policies. "
            "This is **not** the ShellCheck binary."
        ),
        "",
        f"**Pipeline:** `{pipeline}`  ",
        f"**Policies:** {policies}",
        "",
        "| | Count |",
        "|---|---|",
        f"| :white_check_mark: Passed | {result.passed} |",
        f"| :x: Failed | {result.failed} |",
        f"| :fast_forward: Skipped | {result.skipped} |",
        "",
    ]

    coverage = _render_coverage_gaps_markdown(result.unresolved_includes)
    if coverage:
        # Drop the H2 for MR density; keep table and note.
        lines.append("#### Coverage gaps")
        lines.append("")
        lines.extend(coverage[2:])

    if grouped["failed"]:
        lines.append("#### Findings")
        lines.append("")
        for scenario in grouped["failed"]:
            label = html.escape(scenario.policy_id or scenario.feature)
            title = html.escape(scenario.title or scenario.name)
            lines.extend(
                [
                    "<details>",
                    f"<summary><code>{label}</code> — {title}</summary>",
                    "",
                ]
            )
            if scenario.description:
                lines.extend([html.escape(scenario.description), ""])
            if scenario.owasp_cicd:
                lines.append(f"**OWASP CI/CD:** {html.escape(scenario.owasp_cicd)}")
                lines.append("")
            if scenario.iso27001:
                lines.append(f"**ISO 27001:** {html.escape(scenario.iso27001)}")
                lines.append("")
            violations = parse_shell_violations(scenario.message)
            if violations and any(v.job or v.location for v in violations):
                lines.append(
                    render_markdown_table(
                        ["Job", "Location", "Issue", "Inheritance"],
                        _violation_rows(violations, pipeline_file),
                    )
                )
            else:
                lines.extend(
                    [
                        "```",
                        redact_secrets(scenario.message or "Scenario failed."),
                        "```",
                    ]
                )
            lines.extend(["", "</details>", ""])

    if not failures_only and grouped["skipped"]:
        lines.append("#### Skipped policies")
        lines.append("")
        for scenario in grouped["skipped"]:
            reason = redact_secrets(
                scenario.message or "Filter did not match any entities."
            )
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            framework_bits = []
            if scenario.owasp_cicd:
                framework_bits.append(f"OWASP CI/CD: {scenario.owasp_cicd}")
            if scenario.iso27001:
                framework_bits.append(f"ISO 27001: {scenario.iso27001}")
            framework = f" [{'; '.join(framework_bits)}]" if framework_bits else ""
            lines.append(f"- `{label}` — {title}{framework}: {reason}")
        lines.append("")

    if not result.success:
        lines.extend(
            [
                "---",
                "*Merge is blocked until failing shell-check policies are resolved.*",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_shell_check_report(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    output_format: str,
    *,
    failures_only: bool = False,
) -> str | None:
    """Dispatch shell-check report rendering by format."""
    fmt = output_format.lower()
    if fmt == "markdown":
        return render_shell_check_markdown(
            result, pipeline_file, features_dir, failures_only=failures_only
        )
    if fmt == "html":
        return render_shell_check_html(
            result, pipeline_file, features_dir, failures_only=failures_only
        )
    if fmt == "mr-comment":
        return render_shell_check_mr_comment(
            result, pipeline_file, features_dir, failures_only=failures_only
        )
    return None
