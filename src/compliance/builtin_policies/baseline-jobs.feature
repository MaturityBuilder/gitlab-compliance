# METADATA
# title: Baseline job controls
# description: Core job image and execution rules bundled with gitlab-compliance.
# custom:
#   id: GLCI-BUILTIN-BASELINE
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-7
#   iso27001:
#     - A.8.25
#     - A.8.9
Feature: Baseline job controls

# METADATA
# title: Job images must not use the latest tag
# custom:
#   id: GLCI-BUILTIN-BASELINE-01
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

# METADATA
# title: Non-template jobs must define rules
# custom:
#   id: GLCI-BUILTIN-BASELINE-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-1
#     - CICD-SEC-7
#   iso27001:
#     - A.8.9
#     - A.8.32
  Scenario: Non-template jobs must define rules
    Given I have any job defined
    When its name does not start with "."
    Then it must contain rules
