# METADATA
# title: Pipeline safety
# description: Detect pipeline failures with pipefail.
# custom:
#   id: GLCI-SHELL-PIPE
#   severity: HIGH
Feature: Pipeline safety

# METADATA
# title: Pipeline failures are detected
# custom:
#   id: GLCI-SHELL-PIPE-001
#   severity: HIGH
  Scenario: Pipeline failures are detected
    Given I have any job with effective script defined
    When a pipeline is used
    Then pipefail must be enabled

# METADATA
# title: Exit codes are checked across pipelines
# custom:
#   id: GLCI-SHELL-PIPE-002
#   severity: HIGH
  Scenario: Exit codes are checked across pipelines
    Given I have any job with effective script defined
    When a pipeline is used
    Then pipefail must be enabled
