# METADATA
# title: Conditional expression standards
# description: Portable and safely quoted test expressions.
# custom:
#   id: GLCI-SHELL-TEST
#   severity: MEDIUM
Feature: Conditional expressions

# METADATA
# title: Test operators are portable
# custom:
#   id: GLCI-SHELL-TEST-001
#   severity: MEDIUM
  Scenario: Test operators are portable
    Given I have any job with effective script defined
    Then POSIX compliant operators must be used

# METADATA
# title: Variables are quoted in test statements
# custom:
#   id: GLCI-SHELL-TEST-002
#   severity: HIGH
  Scenario: Variables are quoted in test statements
    Given I have any job with effective script defined
    Then variables in test expressions must be quoted
