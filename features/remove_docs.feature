Feature: Remove GitLab Docs block from file

  Scenario: Remove content between GLDOCS_TITLE and GLDOCS_END markers
    Given a file with content between the markers
    When the gitlab_docs_remove_docs function is called
    Then the file should contain only content outside the markers
