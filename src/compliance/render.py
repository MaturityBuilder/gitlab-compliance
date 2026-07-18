"""Render compliance results to multiple output formats."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone

from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.secret_redact import redact_secrets
from src.modules.common import render_markdown_table

LOCATION_RE = re.compile(r"\(([^():]+):(\d+)\)")
GITLAB_SEVERITIES = frozenset({"info", "minor", "major", "critical", "blocker"})
METADATA_SEVERITY_MAP = {
    "blocker": "blocker",
    "critical": "critical",
    "high": "major",
    "medium": "minor",
    "low": "info",
}


def _status_icon(status: str, for_mr: bool = False) -> str:
    if for_mr:
        return {
            "passed": ":white_check_mark:",
            "failed": ":x:",
            "skipped": ":fast_forward:",
        }.get(status, ":grey_question:")
    return {
        "passed": "✅ PASS",
        "failed": "❌ FAIL",
        "skipped": "⏭️ SKIP",
    }.get(status, status.upper())


def _group_by_status(result: ComplianceResult) -> dict[str, list]:
    grouped: dict[str, list] = {"passed": [], "failed": [], "skipped": []}
    for scenario in result.scenario_results:
        grouped.setdefault(scenario.status, []).append(scenario)
    return grouped


def render_compliance_markdown(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
) -> str:
    grouped = _group_by_status(result)
    lines = [
        "# GitLab CI Compliance Report",
        "",
        f"- **Pipeline:** `{pipeline_file}`",
        f"- **Policies:** `{features_dir}`",
        f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Summary",
        "",
        render_markdown_table(
            ["Status", "Count"],
            [
                ["Passed", str(result.passed)],
                ["Failed", str(result.failed)],
                ["Skipped", str(result.skipped)],
                ["Overall", "PASS" if result.success else "FAIL"],
            ],
        ),
        "",
    ]

    for status in ("failed", "skipped", "passed"):
        scenarios = grouped[status]
        if not scenarios:
            continue
        lines.extend([f"## {status.title()} scenarios", ""])
        for scenario in scenarios:
            lines.append(
                f"### {scenario.policy_id or scenario.feature} — {scenario.title or scenario.name}"
            )
            lines.append("")
            lines.append(f"- **Status:** {_status_icon(scenario.status)}")
            if scenario.policy_id:
                lines.append(f"- **Policy ID:** `{scenario.policy_id}`")
            if scenario.description:
                lines.append(f"- **Description:** {scenario.description}")
            if scenario.message:
                lines.append(f"- **Details:** {redact_secrets(scenario.message)}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_compliance_mr_comment(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
) -> str:
    grouped = _group_by_status(result)
    overall = (
        ":white_check_mark: **Compliance passed**"
        if result.success
        else ":x: **Compliance failed**"
    )
    lines = [
        "### GitLab CI Compliance Report",
        "",
        overall,
        "",
        f"**Pipeline:** `{pipeline_file}`  ",
        f"**Policies:** `{features_dir}`",
        "",
        "| | Count |",
        "|---|---|",
        f"| {_status_icon('passed', for_mr=True)} Passed | {result.passed} |",
        f"| {_status_icon('failed', for_mr=True)} Failed | {result.failed} |",
        f"| {_status_icon('skipped', for_mr=True)} Skipped | {result.skipped} |",
        "",
    ]

    if grouped["failed"]:
        lines.append("#### Failed policies")
        lines.append("")
        for scenario in grouped["failed"]:
            label = html.escape(scenario.policy_id or scenario.feature)
            title = html.escape(scenario.title or scenario.name)
            summary = f"<code>{label}</code> — {title}"
            lines.extend(
                [
                    "<details>",
                    f"<summary>{summary}</summary>",
                    "",
                ]
            )
            if scenario.description:
                lines.extend([html.escape(scenario.description), ""])
            lines.extend(
                [
                    "```",
                    redact_secrets(scenario.message or "Scenario failed."),
                    "```",
                    "",
                    "</details>",
                    "",
                ]
            )

    if grouped["skipped"]:
        lines.append("#### Skipped policies")
        lines.append("")
        for scenario in grouped["skipped"]:
            reason = redact_secrets(
                scenario.message or "Filter did not match any entities."
            )
            label = scenario.policy_id or scenario.feature
            title = scenario.title or scenario.name
            lines.append(f"- `{label}` — {title}: {reason}")

    if not result.success:
        lines.extend(
            [
                "",
                "---",
                "*Merge is blocked until failing compliance policies are resolved.*",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_compliance_html(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
) -> str:
    grouped = _group_by_status(result)
    overall_class = "pass" if result.success else "fail"
    overall_label = "Compliance Passed" if result.success else "Compliance Failed"

    def render_scenario_rows(scenarios: list) -> str:
        if not scenarios:
            return "<tr><td colspan='4'>None</td></tr>"
        rows = []
        for scenario in scenarios:
            rows.append(
                "<tr>"
                f"<td><code>{html.escape(scenario.policy_id or '-')}</code></td>"
                f"<td>{html.escape(scenario.feature)}</td>"
                f"<td>{html.escape(scenario.title or scenario.name)}</td>"
                f"<td class='{html.escape(scenario.status)}'>{_status_icon(scenario.status)}</td>"
                "</tr>"
                + (
                    f"<tr><td colspan='4'><pre>{html.escape(redact_secrets(scenario.message))}</pre></td></tr>"
                    if scenario.message
                    else ""
                )
            )
        return "".join(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GitLab CI Compliance Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; color: #1f2937; }}
    .banner.pass {{ background: #def7ec; border: 1px solid #84e1bc; color: #03543f; }}
    .banner.fail {{ background: #fde8e8; border: 1px solid #f98080; color: #9b1c1c; }}
    .banner {{ padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1.5rem; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 0.75rem; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; }}
    td.pass {{ color: #057a55; font-weight: 600; }}
    td.fail {{ color: #c81e1e; font-weight: 600; }}
    td.skipped {{ color: #6b7280; font-weight: 600; }}
    pre {{ white-space: pre-wrap; margin: 0; }}
    .meta {{ color: #6b7280; margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <div class="banner {overall_class}">{overall_label}</div>
  <p class="meta"><strong>Pipeline:</strong> {html.escape(pipeline_file)}<br>
  <strong>Policies:</strong> {html.escape(features_dir)}<br>
  <strong>Generated:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>

  <h2>Summary</h2>
  <table>
    <thead><tr><th>Status</th><th>Count</th></tr></thead>
    <tbody>
      <tr><td>Passed</td><td>{result.passed}</td></tr>
      <tr><td>Failed</td><td>{result.failed}</td></tr>
      <tr><td>Skipped</td><td>{result.skipped}</td></tr>
    </tbody>
  </table>

  <h2>Failed scenarios</h2>
  <table>
    <thead><tr><th>ID</th><th>Feature</th><th>Policy</th><th>Status</th></tr></thead>
    <tbody>{render_scenario_rows(grouped['failed'])}</tbody>
  </table>

  <h2>Skipped scenarios</h2>
  <table>
    <thead><tr><th>ID</th><th>Feature</th><th>Policy</th><th>Status</th></tr></thead>
    <tbody>{render_scenario_rows(grouped['skipped'])}</tbody>
  </table>

  <h2>Passed scenarios</h2>
  <table>
    <thead><tr><th>ID</th><th>Feature</th><th>Policy</th><th>Status</th></tr></thead>
    <tbody>{render_scenario_rows(grouped['passed'])}</tbody>
  </table>
</body>
</html>
"""


def _normalize_repo_path(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    return normalized


def _check_name_for_scenario(scenario: ScenarioResult) -> str:
    if scenario.policy_id:
        return scenario.policy_id
    feature_slug = re.sub(r"[^a-zA-Z0-9]+", "-", scenario.feature).strip("-").lower()
    name_slug = re.sub(r"[^a-zA-Z0-9]+", "-", scenario.name).strip("-").lower()
    return f"compliance/{feature_slug}/{name_slug}"


def _map_severity(status: str, metadata_severity: str) -> str:
    if status == "skipped":
        return "info"
    normalized = metadata_severity.strip().lower()
    if normalized in GITLAB_SEVERITIES:
        return normalized
    if normalized in METADATA_SEVERITY_MAP:
        return METADATA_SEVERITY_MAP[normalized]
    return "major"


def _fingerprint(check_name: str, path: str, line: int, description: str) -> str:
    payload = f"{check_name}|{path}|{line}|{description}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _description_for_scenario(scenario: ScenarioResult) -> str:
    if scenario.message:
        return scenario.message
    if scenario.status == "skipped":
        return (
            scenario.description
            or f"Scenario skipped: {scenario.title or scenario.name}"
        )
    return (
        scenario.description
        or f"Compliance check failed: {scenario.title or scenario.name}"
    )


def _parse_locations(message: str, fallback_path: str) -> list[tuple[str, int]]:
    locations = [
        (_normalize_repo_path(path), int(line))
        for path, line in LOCATION_RE.findall(message)
    ]
    if locations:
        return locations
    return [(_normalize_repo_path(fallback_path), 1)]


def _findings_for_scenario(scenario: ScenarioResult, pipeline_file: str) -> list[dict]:
    check_name = _check_name_for_scenario(scenario)
    description = _description_for_scenario(scenario)
    severity = _map_severity(scenario.status, scenario.severity)
    fallback_path = _normalize_repo_path(
        os.path.relpath(os.path.abspath(pipeline_file))
    )

    findings = []
    for path, line in _parse_locations(scenario.message, fallback_path):
        findings.append(
            {
                "description": description,
                "check_name": check_name,
                "fingerprint": _fingerprint(check_name, path, line, description),
                "severity": severity,
                "location": {
                    "path": path,
                    "lines": {"begin": line},
                },
            }
        )
    return findings


def render_compliance_code_quality(
    result: ComplianceResult,
    pipeline_file: str,
) -> str:
    """Render failed and skipped scenarios as a GitLab Code Quality JSON report."""
    findings: list[dict] = []
    for scenario in result.scenario_results:
        if scenario.status not in ("failed", "skipped"):
            continue
        findings.extend(_findings_for_scenario(scenario, pipeline_file))
    return json.dumps(findings, indent=2) + "\n"


def render_compliance_report(
    result: ComplianceResult,
    pipeline_file: str,
    features_dir: str,
    output_format: str,
) -> str | None:
    fmt = output_format.lower()
    if fmt == "markdown":
        return render_compliance_markdown(result, pipeline_file, features_dir)
    if fmt == "html":
        return render_compliance_html(result, pipeline_file, features_dir)
    if fmt == "mr-comment":
        return render_compliance_mr_comment(result, pipeline_file, features_dir)
    if fmt == "codequality":
        return render_compliance_code_quality(result, pipeline_file)
    return None
