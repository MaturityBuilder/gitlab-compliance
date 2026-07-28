Feature: Service containers must be version-pinned

  Scenario: docker:dind must include a version
    Given I have any job defined
    When it has services
    Then its services must not match "docker:dind$"
    And its services must match "docker:[0-9]+\\.[0-9]+\\.[0-9]+-dind"
