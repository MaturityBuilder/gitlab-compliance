"""Tests for GitHub source links on BUILTIN policy catalog entries."""

from __future__ import annotations

from pathlib import Path

from src.compliance.builtin_policies import BUILTIN_SHELL_POLICIES_DIR
from src.compliance.metadata import build_policy_catalog, format_custom_list
from src.compliance.policy_doc import render_policy_catalog

REPO_ROOT = Path(__file__).resolve().parents[1]
GITHUB_PREFIX = (
    "https://github.com/MaturityBuilder/gitlab-compliance/blob/main/"
    "src/compliance/builtin_policies/"
)


def test_builtin_catalog_markdown_links_to_github():
    catalog = build_policy_catalog(str(BUILTIN_SHELL_POLICIES_DIR))
    md = render_policy_catalog(catalog, str(BUILTIN_SHELL_POLICIES_DIR), "markdown")
    assert "GLCI-BUILTIN-SHELL-QUOTE-01" in md
    assert GITHUB_PREFIX in md
    assert "shell-quoting.feature#L" in md
    assert f"]({GITHUB_PREFIX}" in md
    assert "**Policies directory:** `src/compliance/builtin_policies" in md
    assert "| ID " in md
    assert "| Title " in md
    assert "| Scope " in md
    assert "| Location " in md
    assert "| Severity " in md
    assert "| OWASP CI/CD " in md
    assert "| ISO 27001 " in md
    assert "| Description " in md
    assert "CICD-SEC-" in md
    assert "A.8." in md
    # Index must surface framework tags, not only scenario detail tables.
    index_section = md.split("## Index", 1)[1].split("\n## ", 1)[0]
    assert "CICD-SEC-" in index_section
    assert "A.8." in index_section


def test_builtin_catalog_html_links_to_github():
    catalog = build_policy_catalog(str(BUILTIN_SHELL_POLICIES_DIR))
    html = render_policy_catalog(catalog, str(BUILTIN_SHELL_POLICIES_DIR), "html")
    assert "GLCI-BUILTIN-SHELL-QUOTE-01" in html
    assert GITHUB_PREFIX in html
    assert 'href="' in html and "shell-quoting.feature#L" in html
    assert "<th>Severity</th>" in html
    assert "<th>OWASP CI/CD</th>" in html
    assert "<th>ISO 27001</th>" in html
    assert "<h3>Scenarios</h3>" in html
    assert "CICD-SEC-" in html
    assert "A.8." in html
    assert html.count("<th>OWASP CI/CD</th>") >= 2


def test_non_builtin_id_stays_plain_location(tmp_path):
    # Path mimics a custom policy dir (no builtin_policies segment).
    feature = tmp_path / "custom.feature"
    feature.write_text(
        """\
# METADATA
# title: Custom pack
# custom:
#   id: GLCI-CUSTOM-DEMO
#   severity: LOW
Feature: Custom pack

# METADATA
# title: Custom scenario
# custom:
#   id: GLCI-CUSTOM-DEMO-001
#   severity: LOW
  Scenario: Custom scenario
    Given I have any job defined
""",
        encoding="utf-8",
    )
    catalog = build_policy_catalog(str(tmp_path))
    md = render_policy_catalog(catalog, str(tmp_path), "markdown")
    assert "`GLCI-CUSTOM-DEMO-001`" in md
    assert "github.com/MaturityBuilder/gitlab-compliance" not in md
    assert "`custom.feature:" in md
    assert "| ID " in md


def test_scenarios_table_includes_severity(tmp_path):
    feature = tmp_path / "multi.feature"
    feature.write_text(
        """\
# METADATA
# title: Multi scenario pack
# description: Feature with two scenarios.
# custom:
#   id: GLCI-TEST-MULTI
#   severity: MEDIUM
Feature: Multi scenario pack

# METADATA
# title: First rule
# description: First scenario description.
# custom:
#   id: GLCI-TEST-MULTI-01
#   severity: HIGH
  Scenario: First rule
    Given I have any job defined

# METADATA
# title: Second rule
# description: Second scenario description.
# custom:
#   id: GLCI-TEST-MULTI-02
#   severity: LOW
  Scenario: Second rule
    Given I have any job defined
""",
        encoding="utf-8",
    )
    catalog = build_policy_catalog(str(tmp_path))
    md = render_policy_catalog(catalog, str(tmp_path), "markdown")
    assert "### Scenarios" in md
    assert "| ID " in md and "| Severity " in md
    assert "`GLCI-TEST-MULTI-01`" in md
    assert "`GLCI-TEST-MULTI-02`" in md
    assert "HIGH" in md
    assert "LOW" in md
    assert "First scenario description." in md

    html = render_policy_catalog(catalog, str(tmp_path), "html")
    assert "<th>Severity</th>" in html
    assert "<code>GLCI-TEST-MULTI-01</code>" in html
    assert ">HIGH</td>" in html


def test_format_custom_list_joins_values():
    assert (
        format_custom_list({"owasp_cicd": ["CICD-SEC-3", "CICD-SEC-9"]}, "owasp_cicd")
        == "CICD-SEC-3, CICD-SEC-9"
    )
    assert format_custom_list({"iso27001": "A.8.25"}, "iso27001") == "A.8.25"
    assert format_custom_list({}, "owasp_cicd") == ""
    assert format_custom_list(None, "owasp_cicd") == ""


def test_scenarios_table_includes_framework_tags(tmp_path):
    feature = tmp_path / "mapped.feature"
    feature.write_text(
        """\
# METADATA
# title: Mapped pack
# custom:
#   id: GLCI-TEST-MAP
#   severity: HIGH
Feature: Mapped pack

# METADATA
# title: Mapped scenario
# description: Scenario with framework tags.
# custom:
#   id: GLCI-TEST-MAP-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Mapped scenario
    Given I have any job defined
""",
        encoding="utf-8",
    )
    catalog = build_policy_catalog(str(tmp_path))
    annotation = catalog.features[0].scenarios[0]
    assert annotation.custom["owasp_cicd"] == ["CICD-SEC-3", "CICD-SEC-9"]
    assert annotation.custom["iso27001"] == ["A.8.25", "A.8.9"]

    md = render_policy_catalog(catalog, str(tmp_path), "markdown")
    assert "| OWASP CI/CD " in md
    assert "| ISO 27001 " in md
    assert "CICD-SEC-3, CICD-SEC-9" in md
    assert "A.8.25, A.8.9" in md

    html = render_policy_catalog(catalog, str(tmp_path), "html")
    assert "<th>OWASP CI/CD</th>" in html
    assert "<th>ISO 27001</th>" in html
    assert "CICD-SEC-3, CICD-SEC-9" in html
    assert "A.8.25, A.8.9" in html
