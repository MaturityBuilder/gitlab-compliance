Feature: Compliance report output formats
  As a platform engineer
  I want compliance results in markdown, html, and mr-comment formats
  So that I can publish reports in CI and merge requests

  Scenario: Markdown report is generated for a failing policy run
    When I run compliance with format "markdown" on "sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-report.md"
    Then the report file should exist
    And the report file should contain "GitLab CI Compliance Report"
    And the report file should contain "FAIL"
    And the report file should contain ".gitlab-ci.yml:"

  Scenario: MR comment report is generated for a failing policy run
    When I run compliance with format "mr-comment" on "sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-mr-comment.md"
    Then the report file should exist
    And the report file should contain "Compliance failed"
    And the report file should contain "<details>"
    And the report file should contain ".gitlab-ci.yml:"

  Scenario: HTML report is generated for a passing policy run
    When I run compliance with format "html" on "sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/passing" to "/tmp/compliance-report.html"
    Then the report file should exist
    And the report file should contain "Compliance Passed"
