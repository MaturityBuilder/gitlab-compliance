Feature: Engine skip on empty filter
  Scenario: No jobs in impossible stage
    Given I have any job defined
    When its stage is nonexistent_stage_xyz
    Then it must contain image
