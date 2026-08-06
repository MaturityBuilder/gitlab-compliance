# METADATA
# title: CI script dependency pinning
# description: Supply-chain pinning controls for packages and downloads in CI scripts.
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
Feature: CI script dependency pinning

# METADATA
# title: Downloads must verify checksums
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-01
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: Script downloads must verify checksums
    Given I have any job with effective script defined
    Then script downloads must verify checksums

# METADATA
# title: Disallow remote pipe to shell
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-02
#   severity: HIGH
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-4
#   iso27001:
#     - A.8.28
#     - A.8.25
  Scenario: Scripts must not pipe remote downloads to a shell
    Given I have any job with effective script defined
    Then untrusted remote scripts must not be executed

# METADATA
# title: pip packages must be version-pinned
# description: Applies to both pip and pip3 install commands in job scripts.
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-03
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: pip install must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "pip" must use pinned versions

# METADATA
# title: apk packages must be version-pinned
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-04
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: apk add must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "apk" must use pinned versions

# METADATA
# title: apt packages must be version-pinned
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-05
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: apt-get install must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "apt" must use pinned versions

# METADATA
# title: npm global packages must be version-pinned
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-06
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: npm global installs must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "npm" must use pinned versions

# METADATA
# title: go install must pin versions
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-07
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: go install must pin module versions
    Given I have any job with effective script defined
    Then package installs of type "go" must use pinned versions

# METADATA
# title: git clone must verify revision
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-08
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: git clone must verify commit or tag
    Given I have any job with effective script defined
    Then git clone must verify commit or tag

# METADATA
# title: docker run and pull must pin images
# description: Script docker commands must reference an explicit tag or sha256 digest.
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-09
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: docker run and pull must pin container images
    Given I have any job with effective script defined
    Then docker commands must pin container images to a tag or sha256 digest

# METADATA
# title: yum/dnf packages must be version-pinned
# description: Applies to yum, dnf, and microdnf install commands in job scripts.
# custom:
#   id: GLCI-BUILTIN-SHELL-PIN-10
#   severity: MEDIUM
#   owasp_cicd:
#     - CICD-SEC-3
#     - CICD-SEC-9
#   iso27001:
#     - A.8.25
#     - A.8.9
  Scenario: yum and dnf install must pin package versions
    Given I have any job with effective script defined
    Then package installs of type "yum" must use pinned versions
