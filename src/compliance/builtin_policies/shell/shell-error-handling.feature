# METADATA
# title: Error handling
# description: Strict mode and exit-code handling for GitLab CI job scripts.
# custom:
#   id: GLCI-BUILTIN-SHELL-ERR
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
#     - A.8.25
Feature: Error handling

# METADATA
# title: Scripts use strict mode
# custom:
#   id: GLCI-BUILTIN-SHELL-ERR-01
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Multi-line scripts use strict mode
    Given I have any job with effective script defined
    When the effective script has more than 1 line
    Then the script must enable strict mode options

# METADATA
# title: Commands return meaningful exit codes
# custom:
#   id: GLCI-BUILTIN-SHELL-ERR-02
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Commands return meaningful exit codes
    Given I have any job with effective script defined
    Then failure must be handled explicitly

# METADATA
# title: Functions propagate failures
# custom:
#   id: GLCI-BUILTIN-SHELL-ERR-03
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Functions propagate failures
    Given I have any job with effective script defined
    Then functions must propagate failures
