# METADATA
# title: CI script dependency pinning
# description: Supply-chain pinning controls for packages and downloads in CI scripts.
# custom:
#   id: GLCI-SHELL-PIN
#   severity: HIGH
Feature: CI script dependency pinning

# METADATA
# title: Downloads must verify checksums
# custom:
#   id: GLCI-SHELL-PIN-001
#   severity: HIGH
  Scenario: Script downloads must verify checksums
    Given I have any job with effective script defined
    Then script downloads must verify checksums

# METADATA
# title: Disallow remote pipe to shell
# custom:
#   id: GLCI-SHELL-PIN-002
#   severity: HIGH
  Scenario: Scripts must not pipe remote downloads to a shell
    Given I have any job with effective script defined
    Then untrusted remote scripts must not be executed

# METADATA
# title: pip packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-003
#   severity: MEDIUM
  Scenario: pip install must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "pip" must use pinned versions

# METADATA
# title: apk packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-004
#   severity: MEDIUM
  Scenario: apk add must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "apk" must use pinned versions

# METADATA
# title: apt packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-005
#   severity: MEDIUM
  Scenario: apt-get install must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "apt" must use pinned versions

# METADATA
# title: npm global packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-006
#   severity: MEDIUM
  Scenario: npm global installs must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "npm" must use pinned versions

# METADATA
# title: go install must pin versions
# custom:
#   id: GLCI-SHELL-PIN-007
#   severity: MEDIUM
  Scenario: go install must pin module versions
    Given I have any job with effective script defined
    Then package installs of type "go" must use pinned versions

# METADATA
# title: git clone must verify revision
# custom:
#   id: GLCI-SHELL-PIN-008
#   severity: MEDIUM
  Scenario: git clone must verify commit or tag
    Given I have any job with effective script defined
    Then git clone must verify commit or tag
