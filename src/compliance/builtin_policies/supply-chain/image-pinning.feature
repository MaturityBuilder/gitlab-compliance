# Image pinning with sha256 digest and registry checks

# METADATA
# title: Container images must be pinned
# description: Job images must use sha256 digests instead of mutable tags.
# custom:
#   id: GLCI-BUILTIN-IMAGE
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
Feature: Container images must be pinned

# METADATA
# title: Job images must use sha256 digest
# description: Immutable digest pinning is the default supply-chain control.
# custom:
#   id: GLCI-BUILTIN-IMAGE-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Job images must use sha256 digest
    Given I have container image from "job" defined
    Then it must use sha256 digest

# METADATA
# title: Disallow latest image tags
# description: "Prevents jobs from using mutable latest tags such as docker:latest."
# custom:
#   id: GLCI-BUILTIN-IMAGE-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"

# METADATA
# title: Recommend explicit image version or digest
# description: Ensures every job image includes a version tag or sha256 digest.
# custom:
#   id: GLCI-BUILTIN-IMAGE-03
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Job images must include an explicit version or digest
    Given I have any job defined
    When it has image
    Then its image must match "^[^\\s]+(:[\\w.-]+|@sha256:[a-f0-9]{64})$"

# METADATA
# title: Container images must not lag behind registry latest
# description: API-backed check against external registry tags.
# custom:
#   id: GLCI-BUILTIN-IMAGE-04
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.8
#     - A.8.9
  Scenario: Container images must not lag behind registry latest
    Given I have any container image with release metadata defined
    Then a newer image release must not be available
