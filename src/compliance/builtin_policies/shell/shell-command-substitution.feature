# METADATA
# title: Command substitution standards
# description: Prefer modern dollar-parentheses substitution over backticks.
# custom:
#   id: GLCI-BUILTIN-SHELL-SUB
#   severity: MEDIUM
Feature: Command substitution

# METADATA
# title: Legacy backticks are not used
# custom:
#   id: GLCI-BUILTIN-SHELL-SUB-01
#   severity: MEDIUM
  Scenario: Legacy backticks are not used
    Given I have any job with effective script defined
    Then command substitution must use dollar parentheses

# METADATA
# title: Nested command substitution is readable
# custom:
#   id: GLCI-BUILTIN-SHELL-SUB-02
#   severity: MEDIUM
  Scenario: Nested command substitution is readable
    Given I have any job with effective script defined
    Then nested command substitution must use dollar parentheses
