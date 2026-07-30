# METADATA
# title: Pipeline safety
# description: Detect pipeline failures with pipefail.
# custom:
#   id: GLCI-BUILTIN-SHELL-PIPE
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
Feature: Pipeline safety

# METADATA
# title: Pipeline failures are detected
# custom:
#   id: GLCI-BUILTIN-SHELL-PIPE-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Pipeline failures are detected
    Given I have any job with effective script defined
    When a pipeline is used
    Then pipefail must be enabled

# METADATA
# title: Exit codes are checked across pipelines
# custom:
#   id: GLCI-BUILTIN-SHELL-PIPE-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-7
#   iso27001:
#     - A.8.28
  Scenario: Exit codes are checked across pipelines
    Given I have any job with effective script defined
    When a pipeline is used
    Then pipefail must be enabled
