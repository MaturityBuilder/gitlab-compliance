# METADATA
# title: GitLab project CI/CD security settings
# description: API-backed checks for project-level CI/CD hardening controls.
# custom:
#   id: GLCI-API-HARDENING
#   severity: HIGH
Feature: GitLab project CI/CD security settings

# METADATA
# title: Job logs must not be public
# description: Public job logs can expose secrets and internal build details.
# custom:
#   id: GLCI-API-HARDENING-001
#   severity: HIGH
  Scenario: Job logs must not be public
    Given I have project setting "public_jobs" defined
    Then its value must be false

# METADATA
# title: Auto DevOps must be disabled
# description: Auto DevOps can introduce unmanaged pipeline behavior in regulated environments.
# custom:
#   id: GLCI-API-HARDENING-002
#   severity: MEDIUM
  Scenario: Auto DevOps must be disabled
    Given I have project setting "auto_devops_enabled" defined
    Then its value must be false

# METADATA
# title: Production tokens must be protected and masked
# description: Sensitive CI variables must be protected and masked in job logs.
# custom:
#   id: GLCI-API-HARDENING-003
#   severity: CRITICAL
  Scenario: Production tokens must be protected and masked
    Given I have any project ci variable defined
    When its key matches "^(AWS_|DATABASE_|API_KEY)"
    Then its protected must be true
    And its masked must be true
