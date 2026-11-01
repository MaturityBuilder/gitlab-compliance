# METADATA
# title: Dynamic child pipelines must be resolved
# description: >
#   When a pipeline uses trigger.include artifacts, run compliance after the
#   generator job so the child YAML is on disk and resolved into the stash.
# custom:
#   id: GLCI-EXAMPLE-DYNAMIC-01
#   severity: medium
Feature: Dynamic child pipelines must be resolved

# METADATA
# title: Generated child configs are available
# custom:
#   id: GLCI-EXAMPLE-DYNAMIC-01
  Scenario: Generated child configs are available
    Given I have any dynamic child pipeline defined
    Then it must contain resolved
    And its resolved must be true
