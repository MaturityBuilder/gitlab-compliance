# METADATA
# title: GitLab CI script conventions
# description: CI-specific hygiene for curl and deprecated variables.
# custom:
#   id: GLCI-BUILTIN-SHELL-CI
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.25
#     - A.8.28
Feature: GitLab CI script conventions

# METADATA
# title: curl uses fail flag
# custom:
#   id: GLCI-BUILTIN-SHELL-CI-01
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: curl must use fail flag
    Given I have any job with effective script defined
    Then curl must use fail flag

# METADATA
# title: Deprecated CI_BUILD variables are not used
# custom:
#   id: GLCI-BUILTIN-SHELL-CI-02
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.9
#     - A.8.25
  Scenario: Deprecated CI_BUILD variables must not be used
    Given I have any job with effective script defined
    Then deprecated CI_BUILD variables must not be used

# METADATA
# title: CI variables should be quoted
# custom:
#   id: GLCI-BUILTIN-SHELL-CI-03
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: CI variables should be quoted
    Given I have any job with effective script defined
    Then user supplied variables must be quoted or validated
