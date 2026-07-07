Feature: Swagger-style HTML documentation
  As a developer
  I want pipeline documentation rendered as a Swagger-style HTML page
  So that I can browse CI configuration in a familiar interactive format

  Scenario: HTML page is generated from gitlab-ci config
    Given a gitlab-ci config at ".gitlab-ci.yml"
    When I generate swagger HTML to "/tmp/gitlab-compliance-swagger.html"
    Then the HTML file should exist
    And the HTML file should contain "GitLab Docs"
    And the HTML file should contain "opblock-summary-method"
    And the HTML file should contain "MEGALINTER"

  Scenario: HTML page includes workflow rules when detailed
    Given a gitlab-ci config at ".gitlab-ci.yml"
    When I generate detailed swagger HTML to "/tmp/gitlab-compliance-swagger-detailed.html"
    Then the HTML file should exist
    And the HTML file should contain "Workflow"

  Scenario: Generate command supports html format
    Given a gitlab-ci config at ".gitlab-ci.yml"
    When I run generate with format "html" to "/tmp/gitlab-compliance-generate-format.html"
    Then the HTML file should exist
    And the HTML file should contain "GitLab Docs"
