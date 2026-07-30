# METADATA
# title: Include pinning essentials
# description: Baseline checks for component and fragment version pinning.
# custom:
#   id: GLCI-BUILTIN-INCPIN
#   severity: HIGH
Feature: Include pinning essentials

# METADATA
# title: Component includes must not track a branch
# custom:
#   id: GLCI-BUILTIN-INCPIN-01
#   severity: HIGH
  Scenario: Component includes must not track a branch
    Given I have include type "component" defined
    Then its version must not match "^(main|master|develop)$"

# METADATA
# title: Component includes must use semver
# custom:
#   id: GLCI-BUILTIN-INCPIN-02
#   severity: HIGH
  Scenario: Component includes must use semver
    Given I have include type "component" defined
    Then its version must match "^\\d+\\.\\d+\\.\\d+(-[\\w.]+)?$"
