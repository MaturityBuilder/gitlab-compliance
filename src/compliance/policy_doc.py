"""Render compliance policy catalogs from Conftest-style annotations."""

from __future__ import annotations

import html
import os
from datetime import datetime, timezone

from src.compliance.metadata import (
    PolicyAnnotation,
    PolicyCatalog,
    collect_policy_index,
)


def _relative_path(features_dir: str, feature_file: str) -> str:
    try:
        return os.path.relpath(feature_file, os.path.abspath(features_dir))
    except ValueError:
        return feature_file


def _location(features_dir: str, annotation: PolicyAnnotation) -> str:
    rel_path = _relative_path(features_dir, annotation.feature_file)
    if annotation.line:
        return f"{rel_path}:{annotation.line}"
    return rel_path


def render_policy_catalog_markdown(catalog: PolicyCatalog, features_dir: str) -> str:
    lines = [
        "# GitLab CI Compliance Policy Catalog",
        "",
        f"- **Policies directory:** `{features_dir}`",
        f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Index",
        "",
        "| ID | Title | Scope | Location |",
        "|----|-------|-------|----------|",
    ]

    for policy in collect_policy_index(catalog):
        lines.append(
            f"| `{policy.policy_id}` | {policy.title} | {policy.scope} | `{_location(features_dir, policy)}` |"
        )

    lines.append("")
    for feature in catalog.features:
        rel_feature = _relative_path(features_dir, feature.feature_file)
        lines.extend(
            [
                f"## {feature.feature_name}",
                "",
                f"**File:** `{rel_feature}`",
            ]
        )
        if feature.annotation:
            lines.extend(
                [
                    f"**Feature ID:** `{feature.annotation.policy_id}`",
                    "",
                    feature.annotation.description
                    or "_No feature description provided._",
                    "",
                ]
            )
        if feature.scenarios:
            lines.append("### Scenarios")
            lines.append("")
            for scenario in feature.scenarios:
                lines.extend(
                    [
                        f"#### `{scenario.policy_id}` — {scenario.title}",
                        "",
                        f"- **Location:** `{_location(features_dir, scenario)}`",
                    ]
                )
                if scenario.description:
                    lines.append(f"- **Description:** {scenario.description}")
                if scenario.custom:
                    custom_bits = ", ".join(
                        f"`{key}`: {value}"
                        for key, value in scenario.custom.items()
                        if key != "id"
                    )
                    if custom_bits:
                        lines.append(f"- **Custom:** {custom_bits}")
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_policy_catalog_html(catalog: PolicyCatalog, features_dir: str) -> str:
    index_rows = []
    for policy in collect_policy_index(catalog):
        index_rows.append(
            "<tr>"
            f"<td><code>{html.escape(policy.policy_id)}</code></td>"
            f"<td>{html.escape(policy.title)}</td>"
            f"<td>{html.escape(policy.scope)}</td>"
            f"<td><code>{html.escape(_location(features_dir, policy))}</code></td>"
            "</tr>"
        )

    detail_sections = []
    for feature in catalog.features:
        rel_feature = html.escape(_relative_path(features_dir, feature.feature_file))
        scenario_blocks = []
        for scenario in feature.scenarios:
            custom_html = ""
            if scenario.custom:
                items = "".join(
                    f"<li><code>{html.escape(key)}</code>: {html.escape(str(value))}</li>"
                    for key, value in scenario.custom.items()
                    if key != "id"
                )
                if items:
                    custom_html = f"<ul>{items}</ul>"
            scenario_blocks.append(
                "<section>"
                f"<h4><code>{html.escape(scenario.policy_id)}</code> — {html.escape(scenario.title)}</h4>"
                f"<p><code>{html.escape(_location(features_dir, scenario))}</code></p>"
                f"<p>{html.escape(scenario.description)}</p>"
                f"{custom_html}"
                "</section>"
            )
        detail_sections.append(
            "<section>"
            f"<h2>{html.escape(feature.feature_name)}</h2>"
            f"<p><strong>File:</strong> <code>{rel_feature}</code></p>"
            + (
                f"<p><strong>Feature ID:</strong> <code>{html.escape(feature.annotation.policy_id)}</code></p>"
                f"<p>{html.escape(feature.annotation.description)}</p>"
                if feature.annotation
                else ""
            )
            + "".join(scenario_blocks)
            + "</section>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GitLab CI Compliance Policy Catalog</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; color: #1f2937; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 0.75rem; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; }}
    section {{ margin-bottom: 2rem; }}
    .meta {{ color: #6b7280; margin-bottom: 1.5rem; }}
  </style>
</head>
<body>
  <h1>GitLab CI Compliance Policy Catalog</h1>
  <p class="meta"><strong>Policies:</strong> {html.escape(features_dir)}<br>
  <strong>Generated:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
  <h2>Index</h2>
  <table>
    <thead><tr><th>ID</th><th>Title</th><th>Scope</th><th>Location</th></tr></thead>
    <tbody>{''.join(index_rows)}</tbody>
  </table>
  {''.join(detail_sections)}
</body>
</html>
"""


def render_policy_catalog(
    catalog: PolicyCatalog, features_dir: str, output_format: str
) -> str:
    fmt = output_format.lower()
    if fmt == "html":
        return render_policy_catalog_html(catalog, features_dir)
    return render_policy_catalog_markdown(catalog, features_dir)
