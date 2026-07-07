Feature: Job policy baseline

  Scenario: Non-template jobs must define rules
    Given I have any job defined
    When its name does not start with "."
    Then it must contain rules

  Scenario: Deploy jobs must pin an image
    Given I have any job defined
    When its stage is deploy
    Then it must contain image
