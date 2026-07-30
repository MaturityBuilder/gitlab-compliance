# METADATA
# title: Shell script security
# description: Prevent eval, remote pipe execution, secrets, and unsafe modes.
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-4
#     - CICD-SEC-6
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
#     - A.8.25
Feature: Shell script security

# METADATA
# title: Eval is not used
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-4
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Eval is not used
    Given I have any job with effective script defined
    Then eval must not be used

# METADATA
# title: Untrusted input is not executed
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-4
#   iso27001:
#     - A.8.28
#     - A.8.25
  Scenario: Untrusted input is not executed
    Given I have any job with effective script defined
    Then untrusted remote scripts must not be executed

# METADATA
# title: User input is sanitised
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE-03
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-4
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: User input is sanitised
    Given I have any job with effective script defined
    Then user supplied variables must be quoted or validated

# METADATA
# title: Hardcoded secrets are not present
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE-04
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-6
#   iso27001:
#     - A.8.28
#     - A.5.16
  Scenario: Hardcoded secrets are not present
    Given I have any job with effective script defined
    Then hardcoded secrets must not be present

# METADATA
# title: chmod 777 is not used
# custom:
#   id: GLCI-BUILTIN-SHELL-SAFE-05
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
#     - A.8.9
  Scenario: chmod 777 is not used
    Given I have any job with effective script defined
    Then chmod 777 must not be used
