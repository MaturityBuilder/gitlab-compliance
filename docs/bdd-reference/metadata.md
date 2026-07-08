# Policy Metadata

Policies support [Conftest-style `#
METADATA`](https://www.conftest.dev/documentation/) comments for IDs, titles,
descriptions, and custom fields. This is the gitlab-compliance equivalent of
cataloging and templating policy documentation.

```gherkin
# METADATA
# title: Disallow latest image tags
# description: Prevents jobs from using mutable latest tags.
# custom:
#   id: GLCI-IMAGE-PINNING-001
#   severity: HIGH
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"
```text

## Fields

- **`title`:** Short policy name in reports and catalogs
- **`description`:** Longer explanation for security reviewers
- **`custom.id`:** Stable policy ID (auto-generated if omitted)
- **`custom.severity`:**
  - `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` — used in Code Quality output

Metadata can appear at the **Feature** level (applies to the file) or
immediately above a **Scenario**.

## Policy catalog

Generate a searchable index from annotations:

```bash
gitlab-compliance policies doc -f policies/ -o COMPLIANCE-POLICIES.md
gitlab-compliance policies doc -f policies/ --format html -o
COMPLIANCE-POLICIES.html
```text

Compliance reports (console, markdown, HTML, MR comment, Code Quality) include
policy IDs and titles when metadata is present.

## ID generation

If `custom.id` is omitted, IDs are derived from the feature title and scenario
name (for example `GLCI-IMAGE-PINNING-001`).

See [Examples](../examples/index.md) for annotated policy packs.
