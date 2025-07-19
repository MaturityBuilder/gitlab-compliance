Feature: Add content between markers in a file

  Scenario: File does not exist
    Given a non-existent file path
    When I add content "Hello world!" between markers
    Then the file should be created with the content between markers

  Scenario: File exists without marker block
    Given an existing file without marker block
    When I add content "Inserted content" between markers
    Then the file should contain a new marker block with the content

  Scenario: File exists with existing marker block
    Given a file with existing marker block containing "Old content"
    When I add content "New content" between markers
    Then the content should appear before the end marker
