Feature: Loguru logger configuration

  Scenario: Environment-based log level controls debug logging
    Given LOG_LEVEL is set to "DEBUG"
    When the logger is initialized
    Then debug logs should be visible
