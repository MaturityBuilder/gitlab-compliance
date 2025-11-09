Feature: PrettyTable design
  As a developer
  I want to create a PrettyTable with headers, optional field names, and proper styling
  So that tables are consistent and correctly formatted

  Scenario: Table uses provided field_names
    Given a table is created with headers "Name, Age, City" and field names "First, Years, Location"
    Then the table should have field names "First, Years, Location"
    And the table should have borders enabled
    And all columns should be center-aligned
    And the table style should be "MARKDOWN"

  Scenario: Table uses headers when field_names not provided
    Given a table is created with headers "Name, Age, City" and no field names
    Then the table should have field names "Name, Age, City"
    
    And the table should have borders enabled
    And all columns should be center-aligned
    And the table style should be "MARKDOWN"
