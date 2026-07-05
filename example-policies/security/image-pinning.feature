# METADATA
# title: Container images must be pinned
# description: Job images must use explicit versions or digests instead of floating tags.
# custom:
#   id: GLCI-IMAGE-PINNING
#   severity: HIGH
Feature: Container images must be pinned

# METADATA
# title: Disallow latest image tags
# description: Prevents jobs from using mutable latest tags such as docker:latest.
# custom:
#   id: GLCI-IMAGE-PINNING-001
#   severity: HIGH
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"

# METADATA
# title: Require explicit image version or digest
# description: Ensures every job image includes a version tag or sha256 digest.
# custom:
#   id: GLCI-IMAGE-PINNING-002
#   severity: MEDIUM
  Scenario: Job images must include an explicit version or digest
    Given I have any job defined
    When it has image
    Then its image must match "^[^\\s]+(:[\\w.-]+|@sha256:[a-f0-9]{64})$"
