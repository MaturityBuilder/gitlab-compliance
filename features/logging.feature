Feature: Loguru logging configuration

  Scenario: Default LOG_LEVEL uses INFO
    Given no LOG_LEVEL is provided
    When I log an info message
    Then the output should contain "INFO" and the message

  Scenario: Invalid LOG_LEVEL triggers DEBUG logger
    Given an invalid LOG_LEVEL
    When I log a debug message
    Then the output should contain the bug emoji 🐛 and the debug message
