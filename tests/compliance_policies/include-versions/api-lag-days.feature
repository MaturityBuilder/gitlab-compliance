Feature: Include version policies

  Scenario: Release lag must stay within threshold
    Given I have any include with release metadata defined
    Then its release lag must not exceed 90 days
