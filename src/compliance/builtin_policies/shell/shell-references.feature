# METADATA
# title: Script reference resolution
# description: Detect unresolved GitLab !reference tags in script blocks.
# custom:
#   id: GLCI-BUILTIN-SHELL-REF
#   severity: HIGH
Feature: Script reference resolution

# METADATA
# title: No unresolved script references
# custom:
#   id: GLCI-BUILTIN-SHELL-REF-001
#   severity: HIGH
  Scenario: Scripts must not contain unresolved references
    Given I have any job with effective script defined
    Then unresolved script references must not be present
