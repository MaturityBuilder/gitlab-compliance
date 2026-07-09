# METADATA
# title: Outline metadata example
# custom:
#   id: GLCI-OUTLINE-TEST
#   severity: LOW
Feature: Outline metadata example

# METADATA
# title: Variables must match pattern
# custom:
#   id: GLCI-OUTLINE-TEST-001
#   severity: MEDIUM
  Scenario Outline: Variables must match pattern
    Given I have any variable defined
    When its key is <name>
    Then its value must match "<pattern>"

    Examples:
      | name   | pattern |
      | RUNNER | docker  |
