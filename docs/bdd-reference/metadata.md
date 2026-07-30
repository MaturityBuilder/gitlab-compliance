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
#   id: GLCI-BUILTIN-IMAGE-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"
```

## Fields

- **`title`:** Short policy name in reports and catalogs
- **`description`:** Longer explanation for security reviewers
- **`custom.id`:** Stable policy ID (auto-generated if omitted)
- **`custom.severity`:**
  - `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` — used in Code Quality output
- **`custom.owasp_cicd`:** List of
  [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
  IDs (for example `CICD-SEC-3`). Use this for pipeline risk mapping aimed at
  AppSec and platform teams.
- **`custom.iso27001`:** List of ISO/IEC 27001:2022 Annex A control IDs (for
  example `A.8.25`). Use this for enterprise GRC and audit evidence mapping.

Builtin policies ship with both framework mappings. Custom policy packs may omit
them; empty values are shown as blank cells in the policy catalog.

Metadata can appear at the **Feature** level (applies to the file) or
immediately above a **Scenario**.

## Policy catalog

Generate a searchable index from annotations:

```bash
gitlab-compliance policies doc -f policies/ -o COMPLIANCE-POLICIES.md
gitlab-compliance policies doc -f policies/ --format html -o
COMPLIANCE-POLICIES.html
```

The catalog Index and scenario tables include **OWASP CI/CD** and **ISO 27001**
columns when those custom fields are present. Feature sections also show the
feature-level mappings.

Compliance reports (console, markdown, HTML, MR comment, Code Quality, JUnit)
include policy IDs, titles, and OWASP CI/CD / ISO 27001 mappings when those
metadata fields are present.

## ID generation

If `custom.id` is omitted, IDs are derived from the feature title and scenario
name (for example `GLCI-BUILTIN-IMAGE-01`).

See [Examples](../examples/index.md) for annotated policy packs.
