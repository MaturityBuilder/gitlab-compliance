# METADATA
# title: Conditional expression standards
# description: Portable and safely quoted test expressions.
# custom:
#   id: GLCI-BUILTIN-SHELL-TEST
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
Feature: Conditional expressions

# METADATA
# title: Test operators are portable
# custom:
#   id: GLCI-BUILTIN-SHELL-TEST-01
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Test operators are portable
    Given I have any job with effective script defined
    Then POSIX compliant operators must be used

# METADATA
# title: Variables are quoted in test statements
# custom:
#   id: GLCI-BUILTIN-SHELL-TEST-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Variables are quoted in test statements
    Given I have any job with effective script defined
    Then variables in test expressions must be quoted
