Feature: Include version policies

  Scenario: Project includes with semver refs are valid
    Given I have include type "project" defined
    When its version matches "^\d+\.\d+\.\d+"
    Then it must use valid semver
