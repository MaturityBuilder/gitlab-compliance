# METADATA
# title: Error handling
# description: Strict mode and exit-code handling for GitLab CI job scripts.
# custom:
#   id: GLCI-SHELL-ERR
#   severity: HIGH
Feature: Error handling

# METADATA
# title: Scripts use strict mode
# custom:
#   id: GLCI-SHELL-ERR-001
#   severity: MEDIUM
  Scenario: Multi-line scripts use strict mode
    Given I have any job with effective script defined
    When the effective script has more than 1 line
    Then the script must enable strict mode options

# METADATA
# title: Commands return meaningful exit codes
# custom:
#   id: GLCI-SHELL-ERR-002
#   severity: MEDIUM
  Scenario: Commands return meaningful exit codes
    Given I have any job with effective script defined
    Then failure must be handled explicitly

# METADATA
# title: Functions propagate failures
# custom:
#   id: GLCI-SHELL-ERR-003
#   severity: MEDIUM
  Scenario: Functions propagate failures
    Given I have any job with effective script defined
    Then functions must propagate failures
