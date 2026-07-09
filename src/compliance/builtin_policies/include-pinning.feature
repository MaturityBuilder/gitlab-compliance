# METADATA
# title: Include pinning essentials
# description: Baseline checks for component and fragment version pinning.
# custom:
#   id: GLCI-BUILTIN-INCLUDES
#   severity: HIGH
Feature: Include pinning essentials

  Scenario: Component includes must not track a branch
    Given I have include type "component" defined
    Then its version must not match "^(main|master|develop)$"

  Scenario: Component includes must use semver
    Given I have include type "component" defined
    Then its version must match "^\\d+\\.\\d+\\.\\d+(-[\\w.]+)?$"
