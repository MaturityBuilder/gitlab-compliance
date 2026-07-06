Feature: API connection required

  Scenario: Project setting check needs API connection
    Given I have project setting "public_jobs" defined
    Then its value must be false
