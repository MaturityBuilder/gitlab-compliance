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
    assert "GLCI-BUILTIN-SHELL-QUOTE-001" in md
    assert GITHUB_PREFIX in md
    assert "shell-quoting.feature#L" in md
    assert f"]({GITHUB_PREFIX}" in md


def test_builtin_catalog_html_links_to_github():
    catalog = build_policy_catalog(str(BUILTIN_SHELL_POLICIES_DIR))
    html = render_policy_catalog(catalog, str(BUILTIN_SHELL_POLICIES_DIR), "html")
    assert "GLCI-BUILTIN-SHELL-QUOTE-001" in html
    assert GITHUB_PREFIX in html
    assert 'href="' in html and "shell-quoting.feature#L" in html


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
    assert "**Location:** `custom.feature:" in md
