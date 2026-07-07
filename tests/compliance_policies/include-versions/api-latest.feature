Feature: Include version policies

  Scenario: Outdated semver includes fail latest-release check
    Given I have any include with release metadata defined
    When a newer release is available
    Then it must track the latest release
