# METADATA
# title: Baseline job controls
# description: Core job image and execution rules bundled with gitlab-compliance.
# custom:
#   id: GLCI-BUILTIN-BASELINE
#   severity: HIGH
Feature: Baseline job controls

  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"

  Scenario: Non-template jobs must define rules
    Given I have any job defined
    When its name does not start with "."
    Then it must contain rules
