
Feature: Update marked block in README.md
  As a developer
  I want to insert or update GitLab documentation blocks in README.md
  So that I can manage auto-generated documentation sections

  Background:
    Given I have a test environment set up

  Scenario: Create new README.md with marked block
    Given the file "README.md" does not exist
    When I update the marked block with content "New documentation content"
    Then the file "README.md" should be created
    And the file should contain the marked block


  Scenario: Handle file with no final newline
    Given I have a file "README.md" with content "No newline" and no final newline
    When I update the marked block with content "Block content"
    Then the file should be properly formatted with newlines
