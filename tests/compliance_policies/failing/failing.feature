Feature: Engine failure detection
  Scenario: Jobs must have impossible property
    Given I have any job defined
    Then it must contain totally_fake_property_xyz
