Feature: Compliance engine
  As a developer
  I want the compliance runner to evaluate policy features
  So that consumers can gate GitLab CI configuration

  Scenario: Passing policy succeeds against sample pipeline
    When I run basic compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/passing"
    Then compliance should pass

  Scenario: Failing policy returns non-zero exit
    When I run basic compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/failing"
    Then compliance should fail

  Scenario: Empty WHEN filter skips scenario
    When I run basic compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/skip"
    Then compliance should pass with skipped scenarios

  Scenario: Missing API connection skips API-backed scenario
    When I run api compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/api-missing"
    Then compliance should pass with skipped scenarios

  Scenario: Missing API connection fails in strict mode
    When I run strict api compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/api-missing"
    Then compliance should fail
    And compliance output should mention "API connection info not provided"
