Feature: Variable outline checks

  Scenario Outline: Pipeline variables must match allowed patterns
    Given I have any variable defined
    When its key is <name>
    Then its value must match "<pattern>"

    Examples:
      | name   | pattern |
      | RUNNER | docker  |
