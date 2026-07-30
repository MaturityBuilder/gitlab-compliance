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

_GITHUB_BLOB_BASE = "https://github.com/MaturityBuilder/gitlab-compliance/blob/main/"
_BUILTIN_PATH_MARKER = "src/compliance/builtin_policies/"


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


def _short_location(features_dir: str, annotation: PolicyAnnotation) -> str:
    loc = _location(features_dir, annotation)
    if len(loc) > 24:
        return "…" + loc[-23:]
    return loc


def _builtin_repo_relative_path(feature_file: str) -> str | None:
    """Return repo-relative path under builtin_policies, or None."""
    normalized = os.path.normpath(feature_file).replace("\\", "/")
    marker_index = normalized.find(_BUILTIN_PATH_MARKER)
    if marker_index >= 0:
        return normalized[marker_index:]
    return None


def _github_blob_url(annotation: PolicyAnnotation) -> str | None:
    """Link to GitHub source when the policy ID marks a bundled builtin."""
    if "BUILTIN" not in (annotation.policy_id or ""):
        return None
    repo_rel = _builtin_repo_relative_path(annotation.feature_file)
    if not repo_rel:
        return None
    url = f"{_GITHUB_BLOB_BASE}{repo_rel}"
    if annotation.line:
        url = f"{url}#L{annotation.line}"
    return url


def _format_location_markdown(features_dir: str, annotation: PolicyAnnotation) -> str:
    loc = _location(features_dir, annotation)
    url = _github_blob_url(annotation)
    if url:
        return f"[`{loc}`]({url})"
    return f"`{loc}`"


def _format_short_location_markdown(
    features_dir: str, annotation: PolicyAnnotation
) -> str:
    loc = _short_location(features_dir, annotation)
    url = _github_blob_url(annotation)
    if url:
        return f"[`{loc}`]({url})"
    return f"`{loc}`"


def _format_file_markdown(
    features_dir: str, annotation: PolicyAnnotation | None, feature_file: str
) -> str:
    rel_feature = _relative_path(features_dir, feature_file)
    if annotation is not None:
        url = _github_blob_url(annotation)
        if url:
            # File link without line fragment when possible.
            file_url = url.split("#", 1)[0]
            return f"[`{rel_feature}`]({file_url})"
    return f"`{rel_feature}`"


def _format_location_html(features_dir: str, annotation: PolicyAnnotation) -> str:
    loc = html.escape(_location(features_dir, annotation))
    url = _github_blob_url(annotation)
    if url:
        return f'<a href="{html.escape(url)}"><code>{loc}</code></a>'
    return f"<code>{loc}</code>"


def _format_file_html(
    features_dir: str, annotation: PolicyAnnotation | None, feature_file: str
) -> str:
    rel_feature = html.escape(_relative_path(features_dir, feature_file))
    if annotation is not None:
        url = _github_blob_url(annotation)
        if url:
            file_url = html.escape(url.split("#", 1)[0])
            return f'<a href="{file_url}"><code>{rel_feature}</code></a>'
    return f"<code>{rel_feature}</code>"


def render_policy_catalog_markdown(catalog: PolicyCatalog, features_dir: str) -> str:
    lines = [
        "# GitLab CI Compliance Policy Catalog",
        "",
        f"- **Policies directory:** `{features_dir}`",
        f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Index",
        "",
    ]

    for policy in collect_policy_index(catalog):
        loc = _format_short_location_markdown(features_dir, policy)
        lines.append(
            f"- `{policy.policy_id}` — {policy.title} " f"({policy.scope}, {loc})"
        )

    lines.append("")
    for feature in catalog.features:
        file_ref = _format_file_markdown(
            features_dir, feature.annotation, feature.feature_file
        )
        lines.extend(
            [
                f"## {feature.feature_name}",
                "",
                f"**File:** {file_ref}",
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
                        f"- **Location:** {_format_location_markdown(features_dir, scenario)}",
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
            f"<td>{_format_location_html(features_dir, policy)}</td>"
            "</tr>"
        )

    detail_sections = []
    for feature in catalog.features:
        file_html = _format_file_html(
            features_dir, feature.annotation, feature.feature_file
        )
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
                f"<p>{_format_location_html(features_dir, scenario)}</p>"
                f"<p>{html.escape(scenario.description)}</p>"
                f"{custom_html}"
                "</section>"
            )
        detail_sections.append(
            "<section>"
            f"<h2>{html.escape(feature.feature_name)}</h2>"
            f"<p><strong>File:</strong> {file_html}</p>"
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
