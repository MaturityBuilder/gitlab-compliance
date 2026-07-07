Feature: Include version policies

  Scenario: Branch refs are not valid semver
    Given I have include type "project" defined
    When its version matches "^(main|master)$"
    Then it must use valid semver
