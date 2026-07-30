# METADATA
# title: Service containers must be version-pinned
# description: Service images such as docker:dind must include an explicit version.
# custom:
#   id: GLCI-BUILTIN-SERVICE-PINNING
#   severity: HIGH
Feature: Service containers must be version-pinned

# METADATA
# title: docker:dind must include a version
# custom:
#   id: GLCI-BUILTIN-SERVICE-PINNING-001
#   severity: HIGH
  Scenario: docker:dind must include a version
    Given I have any job defined
    When it has services
    Then its services must not match "docker:dind$"
    And its services must match "docker:[0-9]+\\.[0-9]+\\.[0-9]+-dind"
