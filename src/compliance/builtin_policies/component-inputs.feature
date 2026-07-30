# METADATA
# title: Component input constraints
# description: Advanced Scenario Outline for component inputs and conditional fields.
# custom:
#   id: GLCI-BUILTIN-COMPONENT-INPUTS
#   severity: MEDIUM
Feature: Component input constraints

# METADATA
# title: Component input mode constrains dependent fields
# custom:
#   id: GLCI-BUILTIN-COMPONENT-INPUTS-001
#   severity: MEDIUM
  Scenario Outline: Component input mode constrains dependent fields
    Given I have include type "component" defined
    When the entity input <input> equals <value>
    Then its <conditional key> must match "<conditional value>"

    Examples:
      | input | value   | conditional key | conditional value |
      | mode  | execute | workflow        | trunk,main        |
      | mode  | dry-run | workflow        | gitops            |
