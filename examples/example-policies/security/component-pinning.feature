Feature: CI/CD components must be version-pinned

  Scenario: Component includes must not track a branch
    Given I have include type "component" defined
    Then its version must not match "^(main|master|develop)$"

  Scenario: Component includes must use semver
    Given I have include type "component" defined
    Then its version must match "^\\d+\\.\\d+\\.\\d+(-[\\w.]+)?$"

  Scenario: Component includes must not use latest alias
    Given I have include type "component" defined
    Then its version must not match "^latest$"
