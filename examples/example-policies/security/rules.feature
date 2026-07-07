Feature: Pipeline execution controls

  Scenario: Deploy jobs must define rules
    Given I have any job defined
    When its stage is deploy
    Then it must contain rules
