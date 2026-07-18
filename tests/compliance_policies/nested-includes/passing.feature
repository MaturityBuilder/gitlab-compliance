Feature: Nested local includes surface leaf jobs

  Policies for tests/fixtures/nested-includes. With --include-nested (default
  for check), deep local includes must load so named leaf jobs are found.

  Scenario: Deep security leaf job is present
    Given I have job "deep_sast" defined
    Then it must contain stage

  Scenario: Deep build leaf job is present
    Given I have job "publish_image" defined
    Then it must contain stage

  Scenario: Mid-level security jobs are present
    Given I have job "security_gate" defined
    Then it must contain stage

  Scenario: Mid-level scanners job is present
    Given I have job "secret_scan" defined
    Then it must contain stage

  Scenario: Mid-level build jobs are present
    Given I have job "compile" defined
    Then it must contain stage

  Scenario: Mid-level docker job is present
    Given I have job "docker_build" defined
    Then it must contain stage
