Feature: Pipeline execution controls

  Scenario: Deploy jobs must define rules
    Given I have any job defined
    When its stage is deploy
    Then it must contain rules

  Scenario: Jobs with rules must include conditional guards
    Given I have any job defined
    When it has rules
    Then its rules must match "if:"
