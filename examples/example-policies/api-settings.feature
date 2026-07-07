Feature: Project CI/CD hardening

  Scenario: Public jobs must be disabled
    Given I have project setting "public_jobs" defined
    Then its value must be false

  Scenario: Auto DevOps must be disabled
    Given I have project setting "auto_devops_enabled" defined
    Then its value must be false
