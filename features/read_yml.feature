Feature: Reading YAML files
  As a developer
  I want to read multiple YAML documents from a file
  So that I can process them as a list of dictionaries

  Scenario: Read multiple YAML documents
    Given a YAML file "test_config.yml" with content:
      """
      name: Alice
      age: 30
      ---
      name: Bob
      age: 25
      """
    When I read the YAML file using read_yml
    Then I should get 2 documents
    And the first document should have name "Alice" and age 30
    And the second document should have name "Bob" and age 25
