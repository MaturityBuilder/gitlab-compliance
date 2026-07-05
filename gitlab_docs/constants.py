"""Shared constants for gitlab-docs."""

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

SUPPORTED_OUTPUT_FORMATS = frozenset({"markdown", "html", "json", "csv"})

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
