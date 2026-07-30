# METADATA
# title: Pipeline variable allowlist
# description: Advanced Scenario Outline for required variables and allowed values.
# custom:
#   id: GLCI-BUILTIN-VARIABLES
#   severity: MEDIUM
Feature: Pipeline variable allowlist

# METADATA
# title: Pipeline variables must match allowed patterns
# custom:
#   id: GLCI-BUILTIN-VARIABLES-01
#   severity: MEDIUM
  Scenario Outline: Pipeline variables must match allowed patterns
    Given I have any variable defined
    When its key is <name>
    Then its value must match "<pattern>"

    Examples:
      | name        | pattern                    |
      | APPLICATION | .+                         |
      | ENVIRONMENT | prod,uat,dev               |
      | ROLE        | ^(backend\|frontend\|ops)$ |
