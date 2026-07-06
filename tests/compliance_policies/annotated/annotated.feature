# METADATA
# title: Annotated policy fixture
# description: Used by engine tests to verify policy metadata indexing.
# custom:
#   id: TEST-POLICY-PACK
Feature: Annotated policy fixture

# METADATA
# title: Passing annotated scenario
# description: Ensures metadata IDs appear in compliance output.
# custom:
#   id: TEST-POLICY-001
  Scenario: Passing annotated scenario
    Given I have job "build" defined
    Then it must contain stage
