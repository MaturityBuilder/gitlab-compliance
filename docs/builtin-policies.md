# Builtin Policies Catalog

- **Policies directory:** `/home/me/git/gitlab-compliance/src/compliance/builtin_policies`
- **Generated:** 2026-07-30 20:55:18 UTC

## Index

- `GLCI-BUILTIN-BASELINE` — Baseline job controls (feature, [`baseline-jobs.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L7))
- `GLCI-BUILTIN-BASELINE-001` — Job images must not use the latest tag (scenario, [`baseline-jobs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L14))
- `GLCI-BUILTIN-BASELINE-002` — Non-template jobs must define rules (scenario, [`baseline-jobs.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L24))
- `GLCI-BUILTIN-COMPONENT-INPUTS` — Component input constraints (feature, [`…ponent-inputs.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L7))
- `GLCI-BUILTIN-COMPONENT-INPUTS-001` — Component input mode constrains dependent fields (scenario, [`…onent-inputs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L14))
- `GLCI-BUILTIN-INCLUDES` — Include pinning essentials (feature, [`…clude-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L7))
- `GLCI-BUILTIN-INCLUDES-001` — Component includes must not track a branch (scenario, [`…lude-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14))
- `GLCI-BUILTIN-INCLUDES-002` — Component includes must use semver (scenario, [`…lude-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L23))
- `GLCI-BUILTIN-VARIABLES` — Pipeline variable allowlist (feature, [`…ble-allowlist.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L7))
- `GLCI-BUILTIN-VARIABLES-001` — Pipeline variables must match allowed patterns (scenario, [`…le-allowlist.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L14))
- `GLCI-BUILTIN-IMAGE-PINNING` — Container images must be pinned (feature, [`…image-pinning.feature:9`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L9))
- `GLCI-BUILTIN-IMAGE-PINNING-001` — Job images must use sha256 digest (scenario, [`…mage-pinning.feature:17`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L17))
- `GLCI-BUILTIN-IMAGE-PINNING-002` — Disallow latest image tags (scenario, [`…mage-pinning.feature:27`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L27))
- `GLCI-BUILTIN-IMAGE-PINNING-003` — Recommend explicit image version or digest (scenario, [`…mage-pinning.feature:38`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L38))
- `GLCI-BUILTIN-IMAGE-PINNING-004` — Container images must not lag behind registry latest (scenario, [`…mage-pinning.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L49))
- `GLCI-BUILTIN-INCLUDE-VERSIONS` — Include versions must be valid semver (feature, [`…lude-versions.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L7))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-001` — Project includes must use valid semver (scenario, [`…ude-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-002` — Component includes must use valid semver (scenario, [`…ude-versions.feature:25`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L25))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-003` — Includes must track the latest release (scenario, [`…ude-versions.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L35))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-004` — New releases get a 30-day adoption window (scenario, [`…ude-versions.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L45))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-005` — Includes must stay within 90 days of upstream (scenario, [`…ude-versions.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L55))
- `GLCI-BUILTIN-INCLUDE-VERSIONS-006` — Includes must be within the latest three semver tags (scenario, [`…ude-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65))
- `GLCI-BUILTIN-SERVICE-PINNING` — Service containers must be version-pinned (feature, [`…rvice-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L7))
- `GLCI-BUILTIN-SERVICE-PINNING-001` — docker:dind must include a version (scenario, [`…vice-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L14))
- `GLCI-BUILTIN-SHELL-CI` — GitLab CI script conventions (feature, [`…i-conventions.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L7))
- `GLCI-BUILTIN-SHELL-CI-001` — curl uses fail flag (scenario, [`…-conventions.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L14))
- `GLCI-BUILTIN-SHELL-CI-002` — Deprecated CI_BUILD variables are not used (scenario, [`…-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23))
- `GLCI-BUILTIN-SHELL-CI-003` — CI variables should be quoted (scenario, [`…-conventions.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L32))
- `GLCI-BUILTIN-SHELL-SUB` — Command substitution standards (feature, [`…-substitution.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L7))
- `GLCI-BUILTIN-SHELL-SUB-001` — Legacy backticks are not used (scenario, [`…substitution.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L14))
- `GLCI-BUILTIN-SHELL-SUB-002` — Nested command substitution is readable (scenario, [`…substitution.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L23))
- `GLCI-BUILTIN-SHELL-TEST` — Conditional expression standards (feature, [`…-conditionals.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L7))
- `GLCI-BUILTIN-SHELL-TEST-001` — Test operators are portable (scenario, [`…conditionals.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L14))
- `GLCI-BUILTIN-SHELL-TEST-002` — Variables are quoted in test statements (scenario, [`…conditionals.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L23))
- `GLCI-BUILTIN-SHELL-ERR` — Error handling (feature, [`…rror-handling.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L7))
- `GLCI-BUILTIN-SHELL-ERR-001` — Scripts use strict mode (scenario, [`…ror-handling.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L14))
- `GLCI-BUILTIN-SHELL-ERR-002` — Commands return meaningful exit codes (scenario, [`…ror-handling.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L24))
- `GLCI-BUILTIN-SHELL-ERR-003` — Functions propagate failures (scenario, [`…ror-handling.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L33))
- `GLCI-BUILTIN-SHELL-FILE` — Safe file operations (feature, [`…le-operations.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L7))
- `GLCI-BUILTIN-SHELL-FILE-001` — File paths are quoted (scenario, [`…e-operations.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L14))
- `GLCI-BUILTIN-SHELL-FILE-002` — Temporary files are securely created (scenario, [`…e-operations.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L23))
- `GLCI-BUILTIN-SHELL-FILE-003` — Dangerous rm operations are protected (scenario, [`…e-operations.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L33))
- `GLCI-BUILTIN-SHELL-PIN` — CI script dependency pinning (feature, [`…shell-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L7))
- `GLCI-BUILTIN-SHELL-PIN-001` — Downloads must verify checksums (scenario, [`…hell-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L14))
- `GLCI-BUILTIN-SHELL-PIN-002` — Disallow remote pipe to shell (scenario, [`…hell-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L23))
- `GLCI-BUILTIN-SHELL-PIN-003` — pip packages must be version-pinned (scenario, [`…hell-pinning.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L33))
- `GLCI-BUILTIN-SHELL-PIN-004` — apk packages must be version-pinned (scenario, [`…hell-pinning.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L42))
- `GLCI-BUILTIN-SHELL-PIN-005` — apt packages must be version-pinned (scenario, [`…hell-pinning.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L51))
- `GLCI-BUILTIN-SHELL-PIN-006` — npm global packages must be version-pinned (scenario, [`…hell-pinning.feature:60`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L60))
- `GLCI-BUILTIN-SHELL-PIN-007` — go install must pin versions (scenario, [`…hell-pinning.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L69))
- `GLCI-BUILTIN-SHELL-PIN-008` — git clone must verify revision (scenario, [`…hell-pinning.feature:78`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L78))
- `GLCI-BUILTIN-SHELL-PIN-009` — docker run and pull must pin images (scenario, [`…hell-pinning.feature:88`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L88))
- `GLCI-BUILTIN-SHELL-PIN-010` — yum/dnf packages must be version-pinned (scenario, [`…hell-pinning.feature:98`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L98))
- `GLCI-BUILTIN-SHELL-PIPE` — Pipeline safety (feature, [`…ell-pipelines.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L7))
- `GLCI-BUILTIN-SHELL-PIPE-001` — Pipeline failures are detected (scenario, [`…ll-pipelines.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L14))
- `GLCI-BUILTIN-SHELL-PIPE-002` — Exit codes are checked across pipelines (scenario, [`…ll-pipelines.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L24))
- `GLCI-BUILTIN-SHELL-PORT` — Shell portability (feature, [`…l-portability.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L7))
- `GLCI-BUILTIN-SHELL-PORT-001` — Shebang is valid when present (scenario, [`…-portability.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L14))
- `GLCI-BUILTIN-SHELL-PORT-002` — Bash specific features are declared (scenario, [`…-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23))
- `GLCI-BUILTIN-SHELL-PORT-003` — POSIX compatibility is maintained for sh (scenario, [`…-portability.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L32))
- `GLCI-BUILTIN-SHELL-QUOTE` — Safe variable expansion (feature, [`…shell-quoting.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L7))
- `GLCI-BUILTIN-SHELL-QUOTE-001` — Variables are quoted when expanded (scenario, [`…hell-quoting.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L14))
- `GLCI-BUILTIN-SHELL-QUOTE-002` — Variables used in paths are quoted (scenario, [`…hell-quoting.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L24))
- `GLCI-BUILTIN-SHELL-QUOTE-003` — Command substitutions are quoted (scenario, [`…hell-quoting.feature:34`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L34))
- `GLCI-BUILTIN-SHELL-QUOTE-004` — Arrays are expanded correctly (scenario, [`…hell-quoting.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L44))
- `GLCI-BUILTIN-SHELL-REF` — Script reference resolution (feature, [`…ll-references.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L7))
- `GLCI-BUILTIN-SHELL-REF-001` — No unresolved script references (scenario, [`…l-references.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L14))
- `GLCI-BUILTIN-SHELL-SAFE` — Shell script security (feature, [`…hell-security.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L7))
- `GLCI-BUILTIN-SHELL-SAFE-001` — Eval is not used (scenario, [`…ell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14))
- `GLCI-BUILTIN-SHELL-SAFE-002` — Untrusted input is not executed (scenario, [`…ell-security.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L23))
- `GLCI-BUILTIN-SHELL-SAFE-003` — User input is sanitised (scenario, [`…ell-security.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L32))
- `GLCI-BUILTIN-SHELL-SAFE-004` — Hardcoded secrets are not present (scenario, [`…ell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41))
- `GLCI-BUILTIN-SHELL-SAFE-005` — chmod 777 is not used (scenario, [`…ell-security.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L50))

## Baseline job controls

**File:** [`baseline-jobs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature)
**Feature ID:** `GLCI-BUILTIN-BASELINE`

Core job image and execution rules bundled with gitlab-compliance.

### Scenarios

#### `GLCI-BUILTIN-BASELINE-001` — Job images must not use the latest tag

- **Location:** [`baseline-jobs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-BASELINE-002` — Non-template jobs must define rules

- **Location:** [`baseline-jobs.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L24)
- **Custom:** `severity`: HIGH

## Component input constraints

**File:** [`component-inputs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature)
**Feature ID:** `GLCI-BUILTIN-COMPONENT-INPUTS`

Advanced Scenario Outline for component inputs and conditional fields.

### Scenarios

#### `GLCI-BUILTIN-COMPONENT-INPUTS-001` — Component input mode constrains dependent fields

- **Location:** [`component-inputs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L14)
- **Custom:** `severity`: MEDIUM

## Include pinning essentials

**File:** [`include-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-INCLUDES`

Baseline checks for component and fragment version pinning.

### Scenarios

#### `GLCI-BUILTIN-INCLUDES-001` — Component includes must not track a branch

- **Location:** [`include-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-INCLUDES-002` — Component includes must use semver

- **Location:** [`include-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L23)
- **Custom:** `severity`: HIGH

## Pipeline variable allowlist

**File:** [`variable-allowlist.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature)
**Feature ID:** `GLCI-BUILTIN-VARIABLES`

Advanced Scenario Outline for required variables and allowed values.

### Scenarios

#### `GLCI-BUILTIN-VARIABLES-001` — Pipeline variables must match allowed patterns

- **Location:** [`variable-allowlist.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L14)
- **Custom:** `severity`: MEDIUM

## Container images must be pinned

**File:** [`supply-chain/image-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-IMAGE-PINNING`

Job images must use sha256 digests instead of mutable tags.

### Scenarios

#### `GLCI-BUILTIN-IMAGE-PINNING-001` — Job images must use sha256 digest

- **Location:** [`supply-chain/image-pinning.feature:17`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L17)
- **Description:** Immutable digest pinning is the default supply-chain control.
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-IMAGE-PINNING-002` — Disallow latest image tags

- **Location:** [`supply-chain/image-pinning.feature:27`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L27)
- **Description:** Prevents jobs from using mutable latest tags such as docker:latest.
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-IMAGE-PINNING-003` — Recommend explicit image version or digest

- **Location:** [`supply-chain/image-pinning.feature:38`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L38)
- **Description:** Ensures every job image includes a version tag or sha256 digest.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-IMAGE-PINNING-004` — Container images must not lag behind registry latest

- **Location:** [`supply-chain/image-pinning.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L49)
- **Description:** API-backed check against external registry tags.
- **Custom:** `severity`: MEDIUM

## Include versions must be semver-pinned

**File:** [`supply-chain/include-versions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature)
**Feature ID:** `GLCI-BUILTIN-INCLUDE-VERSIONS`

Project and component includes must pin immutable semver refs.

### Scenarios

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-001` — Project includes must use valid semver

- **Location:** [`supply-chain/include-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15)
- **Description:** Shared fragment refs must be semver tags, not branch names.
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-002` — Component includes must use valid semver

- **Location:** [`supply-chain/include-versions.feature:25`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L25)
- **Description:** CI/CD components must pin explicit semver versions.
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-003` — Includes must track the latest release

- **Location:** [`supply-chain/include-versions.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L35)
- **Description:** API-backed check that semver refs are not behind the newest tag.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-004` — New releases get a 30-day adoption window

- **Location:** [`supply-chain/include-versions.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L45)
- **Description:** Supply chain grace period before requiring upgrade to latest semver.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-005` — Includes must stay within 90 days of upstream

- **Location:** [`supply-chain/include-versions.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L55)
- **Description:** Pinned refs must not trail latest by more than 90 days.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-INCLUDE-VERSIONS-006` — Includes must be within the latest three semver tags

- **Location:** [`supply-chain/include-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)
- **Description:** Pinned refs must rank among the N most recent semver releases.
- **Custom:** `severity`: MEDIUM

## Service containers must be version-pinned

**File:** [`supply-chain/service-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SERVICE-PINNING`

Service images such as docker:dind must include an explicit version.

### Scenarios

#### `GLCI-BUILTIN-SERVICE-PINNING-001` — docker:dind must include a version

- **Location:** [`supply-chain/service-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L14)
- **Custom:** `severity`: HIGH

## GitLab CI script conventions

**File:** [`shell/shell-ci-conventions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-CI`

CI-specific hygiene for curl and deprecated variables.

### Scenarios

#### `GLCI-BUILTIN-SHELL-CI-001` — curl uses fail flag

- **Location:** [`shell/shell-ci-conventions.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L14)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-CI-002` — Deprecated CI_BUILD variables are not used

- **Location:** [`shell/shell-ci-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-CI-003` — CI variables should be quoted

- **Location:** [`shell/shell-ci-conventions.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L32)
- **Custom:** `severity`: MEDIUM

## Command substitution

**File:** [`shell/shell-command-substitution.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SUB`

Prefer modern dollar-parentheses substitution over backticks.

### Scenarios

#### `GLCI-BUILTIN-SHELL-SUB-001` — Legacy backticks are not used

- **Location:** [`shell/shell-command-substitution.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L14)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-SUB-002` — Nested command substitution is readable

- **Location:** [`shell/shell-command-substitution.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L23)
- **Custom:** `severity`: MEDIUM

## Conditional expressions

**File:** [`shell/shell-conditionals.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-TEST`

Portable and safely quoted test expressions.

### Scenarios

#### `GLCI-BUILTIN-SHELL-TEST-001` — Test operators are portable

- **Location:** [`shell/shell-conditionals.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L14)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-TEST-002` — Variables are quoted in test statements

- **Location:** [`shell/shell-conditionals.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L23)
- **Custom:** `severity`: HIGH

## Error handling

**File:** [`shell/shell-error-handling.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-ERR`

Strict mode and exit-code handling for GitLab CI job scripts.

### Scenarios

#### `GLCI-BUILTIN-SHELL-ERR-001` — Scripts use strict mode

- **Location:** [`shell/shell-error-handling.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L14)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-ERR-002` — Commands return meaningful exit codes

- **Location:** [`shell/shell-error-handling.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L24)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-ERR-003` — Functions propagate failures

- **Location:** [`shell/shell-error-handling.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L33)
- **Custom:** `severity`: MEDIUM

## Safe file operations

**File:** [`shell/shell-file-operations.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-FILE`

Quoted paths, secure temps, and protected recursive rm.

### Scenarios

#### `GLCI-BUILTIN-SHELL-FILE-001` — File paths are quoted

- **Location:** [`shell/shell-file-operations.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-FILE-002` — Temporary files are securely created

- **Location:** [`shell/shell-file-operations.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L23)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-FILE-003` — Dangerous rm operations are protected

- **Location:** [`shell/shell-file-operations.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L33)
- **Custom:** `severity`: HIGH

## CI script dependency pinning

**File:** [`shell/shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIN`

Supply-chain pinning controls for packages and downloads in CI scripts.

### Scenarios

#### `GLCI-BUILTIN-SHELL-PIN-001` — Downloads must verify checksums

- **Location:** [`shell/shell-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-PIN-002` — Disallow remote pipe to shell

- **Location:** [`shell/shell-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L23)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-PIN-003` — pip packages must be version-pinned

- **Location:** [`shell/shell-pinning.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L33)
- **Description:** Applies to both pip and pip3 install commands in job scripts.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-004` — apk packages must be version-pinned

- **Location:** [`shell/shell-pinning.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L42)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-005` — apt packages must be version-pinned

- **Location:** [`shell/shell-pinning.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L51)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-006` — npm global packages must be version-pinned

- **Location:** [`shell/shell-pinning.feature:60`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L60)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-007` — go install must pin versions

- **Location:** [`shell/shell-pinning.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L69)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-008` — git clone must verify revision

- **Location:** [`shell/shell-pinning.feature:78`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L78)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-009` — docker run and pull must pin images

- **Location:** [`shell/shell-pinning.feature:88`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L88)
- **Description:** Script docker commands must reference an explicit tag or sha256 digest.
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PIN-010` — yum/dnf packages must be version-pinned

- **Location:** [`shell/shell-pinning.feature:98`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L98)
- **Description:** Applies to yum, dnf, and microdnf install commands in job scripts.
- **Custom:** `severity`: MEDIUM

## Pipeline safety

**File:** [`shell/shell-pipelines.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIPE`

Detect pipeline failures with pipefail.

### Scenarios

#### `GLCI-BUILTIN-SHELL-PIPE-001` — Pipeline failures are detected

- **Location:** [`shell/shell-pipelines.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-PIPE-002` — Exit codes are checked across pipelines

- **Location:** [`shell/shell-pipelines.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L24)
- **Custom:** `severity`: HIGH

## Shell portability

**File:** [`shell/shell-portability.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PORT`

Shebang validity and bash versus POSIX compatibility.

### Scenarios

#### `GLCI-BUILTIN-SHELL-PORT-001` — Shebang is valid when present

- **Location:** [`shell/shell-portability.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L14)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PORT-002` — Bash specific features are declared

- **Location:** [`shell/shell-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23)
- **Custom:** `severity`: MEDIUM

#### `GLCI-BUILTIN-SHELL-PORT-003` — POSIX compatibility is maintained for sh

- **Location:** [`shell/shell-portability.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L32)
- **Custom:** `severity`: MEDIUM

## Safe variable expansion

**File:** [`shell/shell-quoting.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-QUOTE`

ShellCheck-inspired quoting controls for GitLab CI job scripts.

### Scenarios

#### `GLCI-BUILTIN-SHELL-QUOTE-001` — Variables are quoted when expanded

- **Location:** [`shell/shell-quoting.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-QUOTE-002` — Variables used in paths are quoted

- **Location:** [`shell/shell-quoting.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L24)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-QUOTE-003` — Command substitutions are quoted

- **Location:** [`shell/shell-quoting.feature:34`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L34)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-QUOTE-004` — Arrays are expanded correctly

- **Location:** [`shell/shell-quoting.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L44)
- **Custom:** `severity`: MEDIUM

## Script reference resolution

**File:** [`shell/shell-references.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-REF`

Detect unresolved GitLab !reference tags in script blocks.

### Scenarios

#### `GLCI-BUILTIN-SHELL-REF-001` — No unresolved script references

- **Location:** [`shell/shell-references.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L14)
- **Custom:** `severity`: HIGH

## Shell script security

**File:** [`shell/shell-security.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SAFE`

Prevent eval, remote pipe execution, secrets, and unsafe modes.

### Scenarios

#### `GLCI-BUILTIN-SHELL-SAFE-001` — Eval is not used

- **Location:** [`shell/shell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-SAFE-002` — Untrusted input is not executed

- **Location:** [`shell/shell-security.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L23)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-SAFE-003` — User input is sanitised

- **Location:** [`shell/shell-security.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L32)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-SAFE-004` — Hardcoded secrets are not present

- **Location:** [`shell/shell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41)
- **Custom:** `severity`: HIGH

#### `GLCI-BUILTIN-SHELL-SAFE-005` — chmod 777 is not used

- **Location:** [`shell/shell-security.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L50)
- **Custom:** `severity`: MEDIUM
