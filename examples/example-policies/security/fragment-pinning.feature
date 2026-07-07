Feature: Shared CI fragments must be semver-pinned

  Scenario: Project includes must not use branch refs
    Given I have include type "project" defined
    Then its version must not match "^(main|master|develop)$"

  Scenario: Project includes must use valid semver
    Given I have include type "project" defined
    Then its version must match "^\\d+\\.\\d+\\.\\d+"

  Scenario: Security fragments must come from approved projects
    Given I have include type "project" defined
    When its file matches "^security/"
    Then its project must match "^platform/ci-templates$"
