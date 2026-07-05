Feature: Pipeline has expected jobs
  Scenario: gitleaks job defines a stage
    Given I have job "gitleaks" defined
    Then it must contain stage
