Feature: Add content between markers in a file

  Scenario: Create a new file and insert marker block
    Given the file "README.md" does not exist
    When I add between markers
      """
      This is initial content.
      """
    Then the file "README.md" should contain
      """
      This is initial content.
      """

  Scenario: Add content before existing end marker
    Given the file "README.md" contains block
      """
      Existing content.
      """
    When I add between markers
      """
      Additional content.
      """
    Then the file "README.md" should contain
      """
      Existing content.
      Additional content.
      """
