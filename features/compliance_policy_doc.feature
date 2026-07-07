Feature: Compliance policy documentation
  As a platform engineer
  I want policy metadata indexed like Conftest
  So that policies have IDs, titles, and descriptions

  Scenario: Policy catalog is generated from annotated policies
    When I generate a compliance policy catalog from "tests/compliance_policies/annotated" to "/tmp/compliance-policy-catalog.md"
    Then the report file should exist
    And the report file should contain "GitLab CI Compliance Policy Catalog"
    And the report file should contain "TEST-POLICY-001"
    And the report file should contain "Passing annotated scenario"

  Scenario: Compliance output includes policy IDs
    When I run basic compliance on "examples/sample-files/.gitlab-ci.yml" with policies "tests/compliance_policies/annotated"
    Then compliance should pass
    And compliance output should mention "TEST-POLICY-001"
