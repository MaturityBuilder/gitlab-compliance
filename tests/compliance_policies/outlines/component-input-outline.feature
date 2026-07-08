Feature: Component input outline checks

  Scenario Outline: Component input mode constrains dependent fields
    Given I have include type "component" defined
    When the entity input <input> equals <value>
    Then its <conditional key> must match "<conditional value>"

    Examples:
      | input    | value   | conditional key | conditional value |
      | mode     | execute | workflow        | trunk,main        |
      | mode     | dry-run | workflow        | gitops            |
