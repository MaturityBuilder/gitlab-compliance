Feature: YAML environment variable replacement

  Scenario: Replace known variables in a YAML string
    Given a YAML input with !reference tag
    When the YAML is loaded
    Then the variables should be replaced correctly
