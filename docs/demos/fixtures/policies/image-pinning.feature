# METADATA
# title: Container images must be pinned
# description: Job images must use sha256 digests instead of mutable tags.
# custom:
#   id: GLCI-IMAGE-PINNING
#   severity: HIGH
Feature: Container images must be pinned

# METADATA
# title: Job images must use sha256 digest
# description: Immutable digest pinning for demo policies.
# custom:
#   id: GLCI-IMAGE-PINNING-001
#   severity: HIGH
  Scenario: Job images must use sha256 digest
    Given I have container image from "job" defined
    Then it must use sha256 digest

# METADATA
# title: Disallow latest image tags
# description: Prevents jobs from using mutable latest tags.
# custom:
#   id: GLCI-IMAGE-PINNING-002
#   severity: HIGH
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"
