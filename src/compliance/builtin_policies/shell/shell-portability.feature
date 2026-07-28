# METADATA
# title: Shell portability
# description: Shebang validity and bash versus POSIX compatibility.
# custom:
#   id: GLCI-SHELL-PORT
#   severity: MEDIUM
Feature: Shell portability

# METADATA
# title: Shebang is valid when present
# custom:
#   id: GLCI-SHELL-PORT-001
#   severity: MEDIUM
  Scenario: Shebang is valid when present
    Given I have any job with effective script defined
    Then shebang must be valid when present

# METADATA
# title: Bash specific features are declared
# custom:
#   id: GLCI-SHELL-PORT-002
#   severity: MEDIUM
  Scenario: Bash specific features are declared
    Given I have any job with effective script defined
    Then bash specific features must declare bash

# METADATA
# title: POSIX compatibility is maintained for sh
# custom:
#   id: GLCI-SHELL-PORT-003
#   severity: MEDIUM
  Scenario: POSIX compatibility is maintained for sh
    Given I have any job with effective script defined
    Then POSIX shebang scripts must not use bashisms
