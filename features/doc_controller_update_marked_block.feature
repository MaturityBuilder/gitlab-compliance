Feature: Update marked block in a file

  Scenario: Create new file and insert marked block
    Given the file "test_README.md" does not exist
    When I update the block with
      """
      This is some new content.
      """
    Then the file "test_README.md" should contain the marked block with
      """
      This is some new content.
      """

  Scenario: Update existing block in file
    Given the file "test_test_README.md" contains the block
      """
      Old content.
      """
    When I update the block with
      """
      New updated content.
      """
    Then the file "test_README.md" should contain the marked block with
      """
      New updated content.
      """
