"""Shared constants for gitlab-docs / gitlab-compliance."""

GLDOCS_OPENING_MARKER = "[comment]: <> (gitlab-docs-opening-auto-generated)"
GLDOCS_CLOSING_MARKER = "[comment]: <> (gitlab-docs-closing-auto-generated)"

RESERVED_CI_KEYS = frozenset(
    {
        "default",
        "include",
        "stages",
        "variables",
        "workflow",
        "image",
    }
)

# CLI ``generate`` command (Markdown / Swagger HTML).
SUPPORTED_OUTPUT_FORMATS = ("markdown", "html")

# Pipeline table renderer (includes machine-readable exports).
TABLE_RENDER_FORMATS = frozenset({"markdown", "html", "json", "csv"})

DEFAULT_OUTPUT_FILES = {
    "markdown": "README.md",
    "html": "GITLAB-DOCS.html",
}

COMPLIANCE_OUTPUT_FORMATS = ("console", "markdown", "html", "mr-comment", "codequality")

COMPLIANCE_DEFAULT_OUTPUT_FILES = {
    "markdown": "COMPLIANCE-REPORT.md",
    "html": "COMPLIANCE-REPORT.html",
    "mr-comment": "COMPLIANCE-MR-COMMENT.md",
    "codequality": "gl-code-quality-report.json",
}

POLICY_DOC_OUTPUT_FORMATS = ("markdown", "html")

POLICY_DOC_DEFAULT_OUTPUT_FILES = {
    "markdown": "COMPLIANCE-POLICIES.md",
    "html": "COMPLIANCE-POLICIES.html",
}

# Git refs that are valid but not semver (shown as branch/tag, not invalid).
NON_SEMVER_REFS = frozenset(
    {
        "main",
        "master",
        "develop",
        "development",
        "latest",
        "stable",
    }
)
