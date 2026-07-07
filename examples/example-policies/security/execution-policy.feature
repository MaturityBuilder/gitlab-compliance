# METADATA
# title: Pipeline execution controls
# description: Jobs must define rules with conditional guards; deploy jobs are gated.
# custom:
#   id: GLCI-EXECUTION-POLICY
#   severity: HIGH
Feature: Pipeline execution controls

# METADATA
# title: Deploy jobs must define rules
# description: Deploy-stage jobs must not run without explicit rules.
# custom:
#   id: GLCI-EXECUTION-POLICY-001
#   severity: HIGH
  Scenario: Deploy jobs must define rules
    Given I have any job defined
    When its stage is deploy
    Then it must contain rules

# METADATA
# title: Rules must include conditional guards
# description: "Jobs with rules must use if/when guards, not only when: always."
# custom:
#   id: GLCI-EXECUTION-POLICY-002
#   severity: MEDIUM
  Scenario: Jobs with rules must include conditional guards
    Given I have any job defined
    When it has rules
    Then its rules must match "if:"

# METADATA
# title: Non-template jobs must define rules
# description: Every visible job must declare when it runs.
# custom:
#   id: GLCI-EXECUTION-POLICY-003
#   severity: HIGH
  Scenario: Non-template jobs must define rules
    Given I have any job defined
    When its name does not start with "."
    Then it must contain rules
