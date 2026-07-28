Feature: Compliance report output formats
  As a platform engineer
  I want compliance results in markdown, html, and mr-comment formats
  So that I can publish reports in CI and merge requests

  Scenario: Markdown report is generated for a failing policy run
    When I run compliance with format "markdown" on "examples/sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-report.md"
    Then the report file should exist
    And the report file should contain "GitLab CI Compliance Report"
    And the report file should contain "FAIL"
    And the report file should contain ".gitlab-ci.yml:"

  Scenario: MR comment report is generated for a failing policy run
    When I run compliance with format "mr-comment" on "examples/sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-mr-comment.md"
    Then the report file should exist
    And the report file should contain "Compliance failed"
    And the report file should contain "<details>"
    And the report file should contain ".gitlab-ci.yml:"

  Scenario: HTML report is generated for a passing policy run
    When I run compliance with format "html" on "examples/sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/passing" to "/tmp/compliance-report.html"
    Then the report file should exist
    And the report file should contain "Compliance Passed"

  Scenario: Code Quality JSON report is generated for a failing policy run
    When I run compliance with format "codequality" on "examples/sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-codequality.json"
    Then the report file should exist
    And the report file should be valid Code Quality JSON
    And the Code Quality report should contain finding for ".gitlab-ci.yml"

  Scenario: JUnit XML report is generated for a failing policy run
    When I run compliance with format "junit" on "examples/sample-files/.gitlab-ci.yml" policies "tests/compliance_policies/failing" to "/tmp/compliance-junit.xml"
    Then the report file should exist
    And the report file should be valid JUnit XML
    And the JUnit report should contain a failed testcase
