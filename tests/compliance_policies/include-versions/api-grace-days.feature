Feature: Include version policies

  Scenario: Grace period allows recent releases
    Given I have any include with release metadata defined
    Then a newer release must not be available for more than 30 days
