SUPPORTED_OUTPUT_FORMATS = ("markdown", "html")

DEFAULT_OUTPUT_FILES = {
    "markdown": "README.md",
    "html": "gitlab-compliance.html",
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

GITSTRINGS_MARKER_OPEN = (
    "[comment]: <> (gitlab-compliance-gitstrings-opening-auto-generated)"
)
GITSTRINGS_MARKER_CLOSE = (
    "[comment]: <> (gitlab-compliance-gitstrings-closing-auto-generated)"
)
