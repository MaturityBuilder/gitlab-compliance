"""Tests for GitHub source links on BUILTIN policy catalog entries."""

from __future__ import annotations

from pathlib import Path

from src.compliance.builtin_policies import BUILTIN_SHELL_POLICIES_DIR
from src.compliance.metadata import build_policy_catalog
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
    assert "| Description " in md


def test_builtin_catalog_html_links_to_github():
    catalog = build_policy_catalog(str(BUILTIN_SHELL_POLICIES_DIR))
    html = render_policy_catalog(catalog, str(BUILTIN_SHELL_POLICIES_DIR), "html")
    assert "GLCI-BUILTIN-SHELL-QUOTE-01" in html
    assert GITHUB_PREFIX in html
    assert 'href="' in html and "shell-quoting.feature#L" in html
    assert "<th>Severity</th>" in html
    assert "<h3>Scenarios</h3>" in html


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
