Feature: Array formatting for documentation tables
  As a developer
  I want rules and list attributes formatted into readable tables
  So that generated documentation is easier to understand

  Scenario: Rules are rendered as a structured table
    Given rules data:
      """
      [
        {"if": "$CI_COMMIT_TAG", "when": "never"},
        {"if": "$CI_PIPELINE_SOURCE == \"merge_request_event\""}
      ]
      """
    When I build a rules table from the data
    Then the rules table should contain column "if"
    And the rules table should contain column "when"
    And the rules table should contain row value "$CI_COMMIT_TAG"
    And the rules table should contain row value "never"

  Scenario: String lists are rendered as numbered values
    Given a string list "extends, tags, services" with values ".test:rules, .build:python"
    When I format the string list for a table cell
    Then the formatted value should be:
      """
      1. .test:rules
      2. .build:python
      """

  Scenario: Include rules are rendered as compact summaries
    Given rules data:
      """
      [
        {"if": "$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH"}
      ]
      """
    When I format the rules summary
    Then the formatted value should contain "Rule 1:"
    And the formatted value should contain "if=$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH"
