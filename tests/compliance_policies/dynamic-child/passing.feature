# METADATA
# title: Dynamic child pipeline entities
# custom:
#   id: GLCI-TEST-DYNAMIC-01
Feature: Dynamic child pipeline entities

# METADATA
# title: Detect a resolved dynamic child pipeline
# custom:
#   id: GLCI-TEST-DYNAMIC-01
  Scenario: Detect a resolved dynamic child pipeline
    Given I have any dynamic child pipeline defined
    Then it must contain resolved
    And its resolved must be true
