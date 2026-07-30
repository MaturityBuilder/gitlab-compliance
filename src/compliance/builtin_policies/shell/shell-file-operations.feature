# METADATA
# title: Safe file operations
# description: Quoted paths, secure temps, and protected recursive rm.
# custom:
#   id: GLCI-BUILTIN-SHELL-FILE
#   severity: HIGH
Feature: Safe file operations

# METADATA
# title: File paths are quoted
# custom:
#   id: GLCI-BUILTIN-SHELL-FILE-01
#   severity: HIGH
  Scenario: File paths are quoted
    Given I have any job with effective script defined
    Then file paths must be quoted

# METADATA
# title: Temporary files are securely created
# custom:
#   id: GLCI-BUILTIN-SHELL-FILE-02
#   severity: HIGH
  Scenario: Temporary files are securely created
    Given I have any job with effective script defined
    When temporary files are required
    Then mktemp must be used for temporary files

# METADATA
# title: Dangerous rm operations are protected
# custom:
#   id: GLCI-BUILTIN-SHELL-FILE-03
#   severity: HIGH
  Scenario: Dangerous rm operations are protected
    Given I have any job with effective script defined
    When rm is used recursively
    Then path validation must be performed for recursive rm
