# METADATA
# title: Include versions must be valid semver
# description: Project and component includes must pin immutable semver refs.
# custom:
#   id: GLCI-INCLUDE-VERSIONS
#   severity: HIGH
Feature: Include versions must be semver-pinned

# METADATA
# title: Project includes must use valid semver
# description: Shared fragment refs must be semver tags, not branch names.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-001
#   severity: HIGH
  Scenario: Project includes must use valid semver
    Given I have include type "project" defined
    Then it must use valid semver

# METADATA
# title: Component includes must use valid semver
# description: CI/CD components must pin explicit semver versions.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-002
#   severity: HIGH
  Scenario: Component includes must use valid semver
    Given I have include type "component" defined
    Then it must use valid semver

# METADATA
# title: Includes must track the latest release
# description: API-backed check that semver refs are not behind the newest tag.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-003
#   severity: MEDIUM
  Scenario: Includes must not lag behind the latest release
    Given I have any include with release metadata defined
    Then a newer release must not be available

# METADATA
# title: New releases get a 30-day adoption window
# description: Supply chain grace period before requiring upgrade to latest semver.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-004
#   severity: MEDIUM
  Scenario: New releases get a 30-day adoption window
    Given I have any include with release metadata defined
    Then a newer release must not be available for more than 30 days

# METADATA
# title: Includes must stay within 90 days of upstream
# description: Pinned refs must not trail latest by more than 90 days.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-005
#   severity: MEDIUM
  Scenario: Includes must stay within 90 days of upstream
    Given I have any include with release metadata defined
    Then its release lag must not exceed 90 days

# METADATA
# title: Includes must be within the latest three semver tags
# description: Pinned refs must rank among the N most recent semver releases.
# custom:
#   id: GLCI-INCLUDE-VERSIONS-006
#   severity: MEDIUM
  Scenario: Includes must be within the latest three semver tags
    Given I have any include with release metadata defined
    Then it must be within the latest 3 tags
