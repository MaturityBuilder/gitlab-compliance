# METADATA
# title: Safe variable expansion
# description: ShellCheck-inspired quoting controls for GitLab CI job scripts.
# custom:
#   id: GLCI-BUILTIN-SHELL-QUOTE
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
#     - A.8.25
Feature: Safe variable expansion

# METADATA
# title: Variables are quoted when expanded
# custom:
#   id: GLCI-BUILTIN-SHELL-QUOTE-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Variables are quoted when expanded
    Given I have any job with effective script defined
    When a variable is expanded within a command
    Then the variable must be wrapped in double quotes

# METADATA
# title: Variables used in paths are quoted
# custom:
#   id: GLCI-BUILTIN-SHELL-QUOTE-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Variables used in paths are quoted
    Given I have any job with effective script defined
    When variables are used as part of a path
    Then all variables must be safely quoted

# METADATA
# title: Command substitutions are quoted
# custom:
#   id: GLCI-BUILTIN-SHELL-QUOTE-03
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Command substitutions are quoted
    Given I have any job with effective script defined
    When command substitution is used
    Then the result must be quoted unless word splitting is intended

# METADATA
# title: Arrays are expanded correctly
# custom:
#   id: GLCI-BUILTIN-SHELL-QUOTE-04
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Arrays are expanded correctly
    Given I have any job with effective script defined
    When an array is expanded
    Then array "@" syntax must be used where appropriate
