# GitLab CI Compliance Policy Catalog

- **Policies directory:** `src/compliance/builtin_policies`
- **Generated:** 2026-07-30 21:09:59 UTC

## Index

| ID                            | Title                                                | Scope    | Location                                                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-BASELINE`       | Baseline job controls                                | feature  | [`baseline-jobs.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L7)                      |
| `GLCI-BUILTIN-BASELINE-01`    | Job images must not use the latest tag               | scenario | [`baseline-jobs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L14)                    |
| `GLCI-BUILTIN-BASELINE-02`    | Non-template jobs must define rules                  | scenario | [`baseline-jobs.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L24)                    |
| `GLCI-BUILTIN-COMPONENT`      | Component input constraints                          | feature  | [`…ponent-inputs.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L7)                  |
| `GLCI-BUILTIN-COMPONENT-01`   | Component input mode constrains dependent fields     | scenario | [`…onent-inputs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L14)                 |
| `GLCI-BUILTIN-INCPIN`         | Include pinning essentials                           | feature  | [`…clude-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L7)                   |
| `GLCI-BUILTIN-INCPIN-01`      | Component includes must not track a branch           | scenario | [`…lude-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14)                  |
| `GLCI-BUILTIN-INCPIN-02`      | Component includes must use semver                   | scenario | [`…lude-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L23)                  |
| `GLCI-BUILTIN-VARIABLES`      | Pipeline variable allowlist                          | feature  | [`…ble-allowlist.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L7)                |
| `GLCI-BUILTIN-VARIABLES-01`   | Pipeline variables must match allowed patterns       | scenario | [`…le-allowlist.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L14)               |
| `GLCI-BUILTIN-IMAGE`          | Container images must be pinned                      | feature  | [`…image-pinning.feature:9`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L9)        |
| `GLCI-BUILTIN-IMAGE-01`       | Job images must use sha256 digest                    | scenario | [`…mage-pinning.feature:17`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L17)       |
| `GLCI-BUILTIN-IMAGE-02`       | Disallow latest image tags                           | scenario | [`…mage-pinning.feature:27`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L27)       |
| `GLCI-BUILTIN-IMAGE-03`       | Recommend explicit image version or digest           | scenario | [`…mage-pinning.feature:38`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L38)       |
| `GLCI-BUILTIN-IMAGE-04`       | Container images must not lag behind registry latest | scenario | [`…mage-pinning.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L49)       |
| `GLCI-BUILTIN-INCLUDE`        | Include versions must be valid semver                | feature  | [`…lude-versions.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L7)     |
| `GLCI-BUILTIN-INCLUDE-01`     | Project includes must use valid semver               | scenario | [`…ude-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15)    |
| `GLCI-BUILTIN-INCLUDE-02`     | Component includes must use valid semver             | scenario | [`…ude-versions.feature:25`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L25)    |
| `GLCI-BUILTIN-INCLUDE-03`     | Includes must track the latest release               | scenario | [`…ude-versions.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L35)    |
| `GLCI-BUILTIN-INCLUDE-04`     | New releases get a 30-day adoption window            | scenario | [`…ude-versions.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L45)    |
| `GLCI-BUILTIN-INCLUDE-05`     | Includes must stay within 90 days of upstream        | scenario | [`…ude-versions.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L55)    |
| `GLCI-BUILTIN-INCLUDE-06`     | Includes must be within the latest three semver tags | scenario | [`…ude-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)    |
| `GLCI-BUILTIN-SERVICE`        | Service containers must be version-pinned            | feature  | [`…rvice-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L7)      |
| `GLCI-BUILTIN-SERVICE-01`     | docker:dind must include a version                   | scenario | [`…vice-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L14)     |
| `GLCI-BUILTIN-SHELL-CI`       | GitLab CI script conventions                         | feature  | [`…i-conventions.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L7)        |
| `GLCI-BUILTIN-SHELL-CI-01`    | curl uses fail flag                                  | scenario | [`…-conventions.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L14)       |
| `GLCI-BUILTIN-SHELL-CI-02`    | Deprecated CI_BUILD variables are not used           | scenario | [`…-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23)       |
| `GLCI-BUILTIN-SHELL-CI-03`    | CI variables should be quoted                        | scenario | [`…-conventions.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L32)       |
| `GLCI-BUILTIN-SHELL-SUB`      | Command substitution standards                       | feature  | [`…-substitution.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L7)  |
| `GLCI-BUILTIN-SHELL-SUB-01`   | Legacy backticks are not used                        | scenario | [`…substitution.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L14) |
| `GLCI-BUILTIN-SHELL-SUB-02`   | Nested command substitution is readable              | scenario | [`…substitution.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L23) |
| `GLCI-BUILTIN-SHELL-TEST`     | Conditional expression standards                     | feature  | [`…-conditionals.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L7)          |
| `GLCI-BUILTIN-SHELL-TEST-01`  | Test operators are portable                          | scenario | [`…conditionals.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L14)         |
| `GLCI-BUILTIN-SHELL-TEST-02`  | Variables are quoted in test statements              | scenario | [`…conditionals.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L23)         |
| `GLCI-BUILTIN-SHELL-ERR`      | Error handling                                       | feature  | [`…rror-handling.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L7)        |
| `GLCI-BUILTIN-SHELL-ERR-01`   | Scripts use strict mode                              | scenario | [`…ror-handling.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L14)       |
| `GLCI-BUILTIN-SHELL-ERR-02`   | Commands return meaningful exit codes                | scenario | [`…ror-handling.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L24)       |
| `GLCI-BUILTIN-SHELL-ERR-03`   | Functions propagate failures                         | scenario | [`…ror-handling.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L33)       |
| `GLCI-BUILTIN-SHELL-FILE`     | Safe file operations                                 | feature  | [`…le-operations.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L7)       |
| `GLCI-BUILTIN-SHELL-FILE-01`  | File paths are quoted                                | scenario | [`…e-operations.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L14)      |
| `GLCI-BUILTIN-SHELL-FILE-02`  | Temporary files are securely created                 | scenario | [`…e-operations.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L23)      |
| `GLCI-BUILTIN-SHELL-FILE-03`  | Dangerous rm operations are protected                | scenario | [`…e-operations.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L33)      |
| `GLCI-BUILTIN-SHELL-PIN`      | CI script dependency pinning                         | feature  | [`…shell-pinning.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L7)               |
| `GLCI-BUILTIN-SHELL-PIN-01`   | Downloads must verify checksums                      | scenario | [`…hell-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L14)              |
| `GLCI-BUILTIN-SHELL-PIN-02`   | Disallow remote pipe to shell                        | scenario | [`…hell-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L23)              |
| `GLCI-BUILTIN-SHELL-PIN-03`   | pip packages must be version-pinned                  | scenario | [`…hell-pinning.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L33)              |
| `GLCI-BUILTIN-SHELL-PIN-04`   | apk packages must be version-pinned                  | scenario | [`…hell-pinning.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L42)              |
| `GLCI-BUILTIN-SHELL-PIN-05`   | apt packages must be version-pinned                  | scenario | [`…hell-pinning.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L51)              |
| `GLCI-BUILTIN-SHELL-PIN-06`   | npm global packages must be version-pinned           | scenario | [`…hell-pinning.feature:60`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L60)              |
| `GLCI-BUILTIN-SHELL-PIN-07`   | go install must pin versions                         | scenario | [`…hell-pinning.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L69)              |
| `GLCI-BUILTIN-SHELL-PIN-08`   | git clone must verify revision                       | scenario | [`…hell-pinning.feature:78`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L78)              |
| `GLCI-BUILTIN-SHELL-PIN-09`   | docker run and pull must pin images                  | scenario | [`…hell-pinning.feature:88`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L88)              |
| `GLCI-BUILTIN-SHELL-PIN-10`   | yum/dnf packages must be version-pinned              | scenario | [`…hell-pinning.feature:98`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L98)              |
| `GLCI-BUILTIN-SHELL-PIPE`     | Pipeline safety                                      | feature  | [`…ell-pipelines.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L7)             |
| `GLCI-BUILTIN-SHELL-PIPE-01`  | Pipeline failures are detected                       | scenario | [`…ll-pipelines.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L14)            |
| `GLCI-BUILTIN-SHELL-PIPE-02`  | Exit codes are checked across pipelines              | scenario | [`…ll-pipelines.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L24)            |
| `GLCI-BUILTIN-SHELL-PORT`     | Shell portability                                    | feature  | [`…l-portability.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L7)           |
| `GLCI-BUILTIN-SHELL-PORT-01`  | Shebang is valid when present                        | scenario | [`…-portability.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L14)          |
| `GLCI-BUILTIN-SHELL-PORT-02`  | Bash specific features are declared                  | scenario | [`…-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23)          |
| `GLCI-BUILTIN-SHELL-PORT-03`  | POSIX compatibility is maintained for sh             | scenario | [`…-portability.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L32)          |
| `GLCI-BUILTIN-SHELL-QUOTE`    | Safe variable expansion                              | feature  | [`…shell-quoting.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L7)               |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded                   | scenario | [`…hell-quoting.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L14)              |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted                   | scenario | [`…hell-quoting.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L24)              |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted                     | scenario | [`…hell-quoting.feature:34`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L34)              |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly                        | scenario | [`…hell-quoting.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L44)              |
| `GLCI-BUILTIN-SHELL-REF`      | Script reference resolution                          | feature  | [`…ll-references.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L7)            |
| `GLCI-BUILTIN-SHELL-REF-01`   | No unresolved script references                      | scenario | [`…l-references.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L14)           |
| `GLCI-BUILTIN-SHELL-SAFE`     | Shell script security                                | feature  | [`…hell-security.feature:7`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L7)              |
| `GLCI-BUILTIN-SHELL-SAFE-01`  | Eval is not used                                     | scenario | [`…ell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14)             |
| `GLCI-BUILTIN-SHELL-SAFE-02`  | Untrusted input is not executed                      | scenario | [`…ell-security.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L23)             |
| `GLCI-BUILTIN-SHELL-SAFE-03`  | User input is sanitised                              | scenario | [`…ell-security.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L32)             |
| `GLCI-BUILTIN-SHELL-SAFE-04`  | Hardcoded secrets are not present                    | scenario | [`…ell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41)             |
| `GLCI-BUILTIN-SHELL-SAFE-05`  | chmod 777 is not used                                | scenario | [`…ell-security.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L50)             |

## Baseline job controls

**File:** [`baseline-jobs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature)
**Feature ID:** `GLCI-BUILTIN-BASELINE`

Core job image and execution rules bundled with gitlab-compliance.

### Scenarios

| ID                         | Title                                  | Severity | Description | Location                                                                                                                                               |
| -------------------------- | -------------------------------------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-BASELINE-01` | Job images must not use the latest tag | HIGH     |             | [`baseline-jobs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L14) |
| `GLCI-BUILTIN-BASELINE-02` | Non-template jobs must define rules    | HIGH     |             | [`baseline-jobs.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L24) |

## Component input constraints

**File:** [`component-inputs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature)
**Feature ID:** `GLCI-BUILTIN-COMPONENT`

Advanced Scenario Outline for component inputs and conditional fields.

### Scenarios

| ID                          | Title                                            | Severity | Description | Location                                                                                                                                                     |
| --------------------------- | ------------------------------------------------ | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-COMPONENT-01` | Component input mode constrains dependent fields | MEDIUM   |             | [`component-inputs.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L14) |

## Include pinning essentials

**File:** [`include-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-INCPIN`

Baseline checks for component and fragment version pinning.

### Scenarios

| ID                       | Title                                      | Severity | Description | Location                                                                                                                                                   |
| ------------------------ | ------------------------------------------ | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCPIN-01` | Component includes must not track a branch | HIGH     |             | [`include-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14) |
| `GLCI-BUILTIN-INCPIN-02` | Component includes must use semver         | HIGH     |             | [`include-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L23) |

## Pipeline variable allowlist

**File:** [`variable-allowlist.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature)
**Feature ID:** `GLCI-BUILTIN-VARIABLES`

Advanced Scenario Outline for required variables and allowed values.

### Scenarios

| ID                          | Title                                          | Severity | Description | Location                                                                                                                                                         |
| --------------------------- | ---------------------------------------------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-VARIABLES-01` | Pipeline variables must match allowed patterns | MEDIUM   |             | [`variable-allowlist.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L14) |

## Container images must be pinned

**File:** [`supply-chain/image-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-IMAGE`

Job images must use sha256 digests instead of mutable tags.

### Scenarios

| ID                      | Title                                                | Severity | Description                                                         | Location                                                                                                                                                                         |
| ----------------------- | ---------------------------------------------------- | -------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-IMAGE-01` | Job images must use sha256 digest                    | HIGH     | Immutable digest pinning is the default supply-chain control.       | [`supply-chain/image-pinning.feature:17`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L17) |
| `GLCI-BUILTIN-IMAGE-02` | Disallow latest image tags                           | HIGH     | Prevents jobs from using mutable latest tags such as docker:latest. | [`supply-chain/image-pinning.feature:27`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L27) |
| `GLCI-BUILTIN-IMAGE-03` | Recommend explicit image version or digest           | MEDIUM   | Ensures every job image includes a version tag or sha256 digest.    | [`supply-chain/image-pinning.feature:38`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L38) |
| `GLCI-BUILTIN-IMAGE-04` | Container images must not lag behind registry latest | MEDIUM   | API-backed check against external registry tags.                    | [`supply-chain/image-pinning.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L49) |

## Include versions must be semver-pinned

**File:** [`supply-chain/include-versions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature)
**Feature ID:** `GLCI-BUILTIN-INCLUDE`

Project and component includes must pin immutable semver refs.

### Scenarios

| ID                        | Title                                                | Severity | Description                                                          | Location                                                                                                                                                                               |
| ------------------------- | ---------------------------------------------------- | -------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCLUDE-01` | Project includes must use valid semver               | HIGH     | Shared fragment refs must be semver tags, not branch names.          | [`supply-chain/include-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15) |
| `GLCI-BUILTIN-INCLUDE-02` | Component includes must use valid semver             | HIGH     | CI/CD components must pin explicit semver versions.                  | [`supply-chain/include-versions.feature:25`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L25) |
| `GLCI-BUILTIN-INCLUDE-03` | Includes must track the latest release               | MEDIUM   | API-backed check that semver refs are not behind the newest tag.     | [`supply-chain/include-versions.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L35) |
| `GLCI-BUILTIN-INCLUDE-04` | New releases get a 30-day adoption window            | MEDIUM   | Supply chain grace period before requiring upgrade to latest semver. | [`supply-chain/include-versions.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L45) |
| `GLCI-BUILTIN-INCLUDE-05` | Includes must stay within 90 days of upstream        | MEDIUM   | Pinned refs must not trail latest by more than 90 days.              | [`supply-chain/include-versions.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L55) |
| `GLCI-BUILTIN-INCLUDE-06` | Includes must be within the latest three semver tags | MEDIUM   | Pinned refs must rank among the N most recent semver releases.       | [`supply-chain/include-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65) |

## Service containers must be version-pinned

**File:** [`supply-chain/service-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SERVICE`

Service images such as docker:dind must include an explicit version.

### Scenarios

| ID                        | Title                              | Severity | Description | Location                                                                                                                                                                             |
| ------------------------- | ---------------------------------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SERVICE-01` | docker:dind must include a version | HIGH     |             | [`supply-chain/service-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L14) |

## GitLab CI script conventions

**File:** [`shell/shell-ci-conventions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-CI`

CI-specific hygiene for curl and deprecated variables.

### Scenarios

| ID                         | Title                                      | Severity | Description | Location                                                                                                                                                                         |
| -------------------------- | ------------------------------------------ | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-CI-01` | curl uses fail flag                        | MEDIUM   |             | [`shell/shell-ci-conventions.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L14) |
| `GLCI-BUILTIN-SHELL-CI-02` | Deprecated CI_BUILD variables are not used | MEDIUM   |             | [`shell/shell-ci-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23) |
| `GLCI-BUILTIN-SHELL-CI-03` | CI variables should be quoted              | MEDIUM   |             | [`shell/shell-ci-conventions.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L32) |

## Command substitution

**File:** [`shell/shell-command-substitution.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SUB`

Prefer modern dollar-parentheses substitution over backticks.

### Scenarios

| ID                          | Title                                   | Severity | Description | Location                                                                                                                                                                                     |
| --------------------------- | --------------------------------------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SUB-01` | Legacy backticks are not used           | MEDIUM   |             | [`shell/shell-command-substitution.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L14) |
| `GLCI-BUILTIN-SHELL-SUB-02` | Nested command substitution is readable | MEDIUM   |             | [`shell/shell-command-substitution.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L23) |

## Conditional expressions

**File:** [`shell/shell-conditionals.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-TEST`

Portable and safely quoted test expressions.

### Scenarios

| ID                           | Title                                   | Severity | Description | Location                                                                                                                                                                     |
| ---------------------------- | --------------------------------------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-TEST-01` | Test operators are portable             | MEDIUM   |             | [`shell/shell-conditionals.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L14) |
| `GLCI-BUILTIN-SHELL-TEST-02` | Variables are quoted in test statements | HIGH     |             | [`shell/shell-conditionals.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L23) |

## Error handling

**File:** [`shell/shell-error-handling.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-ERR`

Strict mode and exit-code handling for GitLab CI job scripts.

### Scenarios

| ID                          | Title                                 | Severity | Description | Location                                                                                                                                                                         |
| --------------------------- | ------------------------------------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-ERR-01` | Scripts use strict mode               | MEDIUM   |             | [`shell/shell-error-handling.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L14) |
| `GLCI-BUILTIN-SHELL-ERR-02` | Commands return meaningful exit codes | MEDIUM   |             | [`shell/shell-error-handling.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L24) |
| `GLCI-BUILTIN-SHELL-ERR-03` | Functions propagate failures          | MEDIUM   |             | [`shell/shell-error-handling.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L33) |

## Safe file operations

**File:** [`shell/shell-file-operations.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-FILE`

Quoted paths, secure temps, and protected recursive rm.

### Scenarios

| ID                           | Title                                 | Severity | Description | Location                                                                                                                                                                           |
| ---------------------------- | ------------------------------------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-FILE-01` | File paths are quoted                 | HIGH     |             | [`shell/shell-file-operations.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L14) |
| `GLCI-BUILTIN-SHELL-FILE-02` | Temporary files are securely created  | HIGH     |             | [`shell/shell-file-operations.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L23) |
| `GLCI-BUILTIN-SHELL-FILE-03` | Dangerous rm operations are protected | HIGH     |             | [`shell/shell-file-operations.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L33) |

## CI script dependency pinning

**File:** [`shell/shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIN`

Supply-chain pinning controls for packages and downloads in CI scripts.

### Scenarios

| ID                          | Title                                      | Severity | Description                                                             | Location                                                                                                                                                           |
| --------------------------- | ------------------------------------------ | -------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-PIN-01` | Downloads must verify checksums            | HIGH     |                                                                         | [`shell/shell-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L14) |
| `GLCI-BUILTIN-SHELL-PIN-02` | Disallow remote pipe to shell              | HIGH     |                                                                         | [`shell/shell-pinning.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L23) |
| `GLCI-BUILTIN-SHELL-PIN-03` | pip packages must be version-pinned        | MEDIUM   | Applies to both pip and pip3 install commands in job scripts.           | [`shell/shell-pinning.feature:33`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L33) |
| `GLCI-BUILTIN-SHELL-PIN-04` | apk packages must be version-pinned        | MEDIUM   |                                                                         | [`shell/shell-pinning.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L42) |
| `GLCI-BUILTIN-SHELL-PIN-05` | apt packages must be version-pinned        | MEDIUM   |                                                                         | [`shell/shell-pinning.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L51) |
| `GLCI-BUILTIN-SHELL-PIN-06` | npm global packages must be version-pinned | MEDIUM   |                                                                         | [`shell/shell-pinning.feature:60`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L60) |
| `GLCI-BUILTIN-SHELL-PIN-07` | go install must pin versions               | MEDIUM   |                                                                         | [`shell/shell-pinning.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L69) |
| `GLCI-BUILTIN-SHELL-PIN-08` | git clone must verify revision             | MEDIUM   |                                                                         | [`shell/shell-pinning.feature:78`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L78) |
| `GLCI-BUILTIN-SHELL-PIN-09` | docker run and pull must pin images        | MEDIUM   | Script docker commands must reference an explicit tag or sha256 digest. | [`shell/shell-pinning.feature:88`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L88) |
| `GLCI-BUILTIN-SHELL-PIN-10` | yum/dnf packages must be version-pinned    | MEDIUM   | Applies to yum, dnf, and microdnf install commands in job scripts.      | [`shell/shell-pinning.feature:98`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L98) |

## Pipeline safety

**File:** [`shell/shell-pipelines.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIPE`

Detect pipeline failures with pipefail.

### Scenarios

| ID                           | Title                                   | Severity | Description | Location                                                                                                                                                               |
| ---------------------------- | --------------------------------------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PIPE-01` | Pipeline failures are detected          | HIGH     |             | [`shell/shell-pipelines.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L14) |
| `GLCI-BUILTIN-SHELL-PIPE-02` | Exit codes are checked across pipelines | HIGH     |             | [`shell/shell-pipelines.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L24) |

## Shell portability

**File:** [`shell/shell-portability.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PORT`

Shebang validity and bash versus POSIX compatibility.

### Scenarios

| ID                           | Title                                    | Severity | Description | Location                                                                                                                                                                   |
| ---------------------------- | ---------------------------------------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PORT-01` | Shebang is valid when present            | MEDIUM   |             | [`shell/shell-portability.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L14) |
| `GLCI-BUILTIN-SHELL-PORT-02` | Bash specific features are declared      | MEDIUM   |             | [`shell/shell-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23) |
| `GLCI-BUILTIN-SHELL-PORT-03` | POSIX compatibility is maintained for sh | MEDIUM   |             | [`shell/shell-portability.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L32) |

## Safe variable expansion

**File:** [`shell/shell-quoting.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-QUOTE`

ShellCheck-inspired quoting controls for GitLab CI job scripts.

### Scenarios

| ID                            | Title                              | Severity | Description | Location                                                                                                                                                           |
| ----------------------------- | ---------------------------------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded | HIGH     |             | [`shell/shell-quoting.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L14) |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted | HIGH     |             | [`shell/shell-quoting.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L24) |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted   | HIGH     |             | [`shell/shell-quoting.feature:34`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L34) |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly      | MEDIUM   |             | [`shell/shell-quoting.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L44) |

## Script reference resolution

**File:** [`shell/shell-references.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-REF`

Detect unresolved GitLab !reference tags in script blocks.

### Scenarios

| ID                          | Title                           | Severity | Description | Location                                                                                                                                                                 |
| --------------------------- | ------------------------------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-REF-01` | No unresolved script references | HIGH     |             | [`shell/shell-references.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L14) |

## Shell script security

**File:** [`shell/shell-security.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SAFE`

Prevent eval, remote pipe execution, secrets, and unsafe modes.

### Scenarios

| ID                           | Title                             | Severity | Description | Location                                                                                                                                                             |
| ---------------------------- | --------------------------------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SAFE-01` | Eval is not used                  | HIGH     |             | [`shell/shell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14) |
| `GLCI-BUILTIN-SHELL-SAFE-02` | Untrusted input is not executed   | HIGH     |             | [`shell/shell-security.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L23) |
| `GLCI-BUILTIN-SHELL-SAFE-03` | User input is sanitised           | HIGH     |             | [`shell/shell-security.feature:32`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L32) |
| `GLCI-BUILTIN-SHELL-SAFE-04` | Hardcoded secrets are not present | HIGH     |             | [`shell/shell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41) |
| `GLCI-BUILTIN-SHELL-SAFE-05` | chmod 777 is not used             | MEDIUM   |             | [`shell/shell-security.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L50) |
