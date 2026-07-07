Feature: Include version policies

  Scenario: Includes must be within the latest three semver tags
    Given I have any include with release metadata defined
    Then it must be within the latest 3 tags
