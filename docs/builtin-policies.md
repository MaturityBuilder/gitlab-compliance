# GitLab CI Compliance Policy Catalog

- **Policies directory:** `src/compliance/builtin_policies`
- **Generated:** 2026-07-30 21:24:13 UTC

## Index

| ID                            | Title                                                | Scope    | OWASP CI/CD                        | ISO 27001             | Location                                                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------- | -------- | ---------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-BASELINE`       | Baseline job controls                                | feature  | CICD-SEC-3, CICD-SEC-7             | A.8.25, A.8.9         | [`baseline-jobs.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L13)                    |
| `GLCI-BUILTIN-BASELINE-01`    | Job images must not use the latest tag               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`baseline-jobs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L26)                    |
| `GLCI-BUILTIN-BASELINE-02`    | Non-template jobs must define rules                  | scenario | CICD-SEC-1, CICD-SEC-7             | A.8.9, A.8.32         | [`baseline-jobs.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L42)                    |
| `GLCI-BUILTIN-COMPONENT`      | Component input constraints                          | feature  | CICD-SEC-7, CICD-SEC-8             | A.8.9, A.8.25         | [`…onent-inputs.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L13)                 |
| `GLCI-BUILTIN-COMPONENT-01`   | Component input mode constrains dependent fields     | scenario | CICD-SEC-7, CICD-SEC-8             | A.8.9, A.8.25         | [`…onent-inputs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L26)                 |
| `GLCI-BUILTIN-INCPIN`         | Include pinning essentials                           | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14)                  |
| `GLCI-BUILTIN-INCPIN-01`      | Component includes must not track a branch           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:28`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L28)                  |
| `GLCI-BUILTIN-INCPIN-02`      | Component includes must use semver                   | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L44)                  |
| `GLCI-BUILTIN-VARIABLES`      | Pipeline variable allowlist                          | feature  | CICD-SEC-7                         | A.8.9                 | [`…le-allowlist.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L11)               |
| `GLCI-BUILTIN-VARIABLES-01`   | Pipeline variables must match allowed patterns       | scenario | CICD-SEC-7                         | A.8.9                 | [`…le-allowlist.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L22)               |
| `GLCI-BUILTIN-IMAGE`          | Container images must be pinned                      | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L15)       |
| `GLCI-BUILTIN-IMAGE-01`       | Job images must use sha256 digest                    | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:29`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L29)       |
| `GLCI-BUILTIN-IMAGE-02`       | Disallow latest image tags                           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L45)       |
| `GLCI-BUILTIN-IMAGE-03`       | Recommend explicit image version or digest           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:62`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L62)       |
| `GLCI-BUILTIN-IMAGE-04`       | Container images must not lag behind registry latest | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…mage-pinning.feature:80`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L80)       |
| `GLCI-BUILTIN-INCLUDE`        | Include versions must be valid semver                | feature  | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15)    |
| `GLCI-BUILTIN-INCLUDE-01`     | Project includes must use valid semver               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:30`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L30)    |
| `GLCI-BUILTIN-INCLUDE-02`     | Component includes must use valid semver             | scenario | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:48`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L48)    |
| `GLCI-BUILTIN-INCLUDE-03`     | Includes must track the latest release               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)    |
| `GLCI-BUILTIN-INCLUDE-04`     | New releases get a 30-day adoption window            | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:82`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L82)    |
| `GLCI-BUILTIN-INCLUDE-05`     | Includes must stay within 90 days of upstream        | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:99`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L99)    |
| `GLCI-BUILTIN-INCLUDE-06`     | Includes must be within the latest three semver tags | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…de-versions.feature:116`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L116)   |
| `GLCI-BUILTIN-SERVICE`        | Service containers must be version-pinned            | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…vice-pinning.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L13)     |
| `GLCI-BUILTIN-SERVICE-01`     | docker:dind must include a version                   | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…vice-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L26)     |
| `GLCI-BUILTIN-SHELL-CI`       | GitLab CI script conventions                         | feature  | CICD-SEC-7                         | A.8.25, A.8.28        | [`…-conventions.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L12)       |
| `GLCI-BUILTIN-SHELL-CI-01`    | curl uses fail flag                                  | scenario | CICD-SEC-7                         | A.8.28                | [`…-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23)       |
| `GLCI-BUILTIN-SHELL-CI-02`    | Deprecated CI_BUILD variables are not used           | scenario | CICD-SEC-7                         | A.8.9, A.8.25         | [`…-conventions.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L37)       |
| `GLCI-BUILTIN-SHELL-CI-03`    | CI variables should be quoted                        | scenario | CICD-SEC-7                         | A.8.28                | [`…-conventions.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L50)       |
| `GLCI-BUILTIN-SHELL-SUB`      | Command substitution standards                       | feature  | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L11) |
| `GLCI-BUILTIN-SHELL-SUB-01`   | Legacy backticks are not used                        | scenario | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L22) |
| `GLCI-BUILTIN-SHELL-SUB-02`   | Nested command substitution is readable              | scenario | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L35) |
| `GLCI-BUILTIN-SHELL-TEST`     | Conditional expression standards                     | feature  | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L11)         |
| `GLCI-BUILTIN-SHELL-TEST-01`  | Test operators are portable                          | scenario | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L22)         |
| `GLCI-BUILTIN-SHELL-TEST-02`  | Variables are quoted in test statements              | scenario | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L35)         |
| `GLCI-BUILTIN-SHELL-ERR`      | Error handling                                       | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…ror-handling.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L12)       |
| `GLCI-BUILTIN-SHELL-ERR-01`   | Scripts use strict mode                              | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L23)       |
| `GLCI-BUILTIN-SHELL-ERR-02`   | Commands return meaningful exit codes                | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L37)       |
| `GLCI-BUILTIN-SHELL-ERR-03`   | Functions propagate failures                         | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L50)       |
| `GLCI-BUILTIN-SHELL-FILE`     | Safe file operations                                 | feature  | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L11)      |
| `GLCI-BUILTIN-SHELL-FILE-01`  | File paths are quoted                                | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L22)      |
| `GLCI-BUILTIN-SHELL-FILE-02`  | Temporary files are securely created                 | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L35)      |
| `GLCI-BUILTIN-SHELL-FILE-03`  | Dangerous rm operations are protected                | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L49)      |
| `GLCI-BUILTIN-SHELL-PIN`      | CI script dependency pinning                         | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L13)              |
| `GLCI-BUILTIN-SHELL-PIN-01`   | Downloads must verify checksums                      | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L26)              |
| `GLCI-BUILTIN-SHELL-PIN-02`   | Disallow remote pipe to shell                        | scenario | CICD-SEC-3, CICD-SEC-4             | A.8.28, A.8.25        | [`…hell-pinning.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L41)              |
| `GLCI-BUILTIN-SHELL-PIN-03`   | pip packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:57`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L57)              |
| `GLCI-BUILTIN-SHELL-PIN-04`   | apk packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:72`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L72)              |
| `GLCI-BUILTIN-SHELL-PIN-05`   | apt packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:87`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L87)              |
| `GLCI-BUILTIN-SHELL-PIN-06`   | npm global packages must be version-pinned           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:102`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L102)             |
| `GLCI-BUILTIN-SHELL-PIN-07`   | go install must pin versions                         | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:117`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L117)             |
| `GLCI-BUILTIN-SHELL-PIN-08`   | git clone must verify revision                       | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:132`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L132)             |
| `GLCI-BUILTIN-SHELL-PIN-09`   | docker run and pull must pin images                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:148`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L148)             |
| `GLCI-BUILTIN-SHELL-PIN-10`   | yum/dnf packages must be version-pinned              | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:164`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L164)             |
| `GLCI-BUILTIN-SHELL-PIPE`     | Pipeline safety                                      | feature  | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L11)            |
| `GLCI-BUILTIN-SHELL-PIPE-01`  | Pipeline failures are detected                       | scenario | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L22)            |
| `GLCI-BUILTIN-SHELL-PIPE-02`  | Exit codes are checked across pipelines              | scenario | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:36`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L36)            |
| `GLCI-BUILTIN-SHELL-PORT`     | Shell portability                                    | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L12)          |
| `GLCI-BUILTIN-SHELL-PORT-01`  | Shebang is valid when present                        | scenario | CICD-SEC-7                         | A.8.28                | [`…-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23)          |
| `GLCI-BUILTIN-SHELL-PORT-02`  | Bash specific features are declared                  | scenario | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L37)          |
| `GLCI-BUILTIN-SHELL-PORT-03`  | POSIX compatibility is maintained for sh             | scenario | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L51)          |
| `GLCI-BUILTIN-SHELL-QUOTE`    | Safe variable expansion                              | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…hell-quoting.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L12)              |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded                   | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L23)              |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted                   | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L37)              |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted                     | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L51)              |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly                        | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L65)              |
| `GLCI-BUILTIN-SHELL-REF`      | Script reference resolution                          | feature  | CICD-SEC-7                         | A.8.9, A.8.25         | [`…l-references.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L12)           |
| `GLCI-BUILTIN-SHELL-REF-01`   | No unresolved script references                      | scenario | CICD-SEC-7                         | A.8.9, A.8.25         | [`…l-references.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L24)           |
| `GLCI-BUILTIN-SHELL-SAFE`     | Shell script security                                | feature  | CICD-SEC-4, CICD-SEC-6, CICD-SEC-7 | A.8.28, A.8.25        | [`…ell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14)             |
| `GLCI-BUILTIN-SHELL-SAFE-01`  | Eval is not used                                     | scenario | CICD-SEC-4, CICD-SEC-7             | A.8.28                | [`…ell-security.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L26)             |
| `GLCI-BUILTIN-SHELL-SAFE-02`  | Untrusted input is not executed                      | scenario | CICD-SEC-3, CICD-SEC-4             | A.8.28, A.8.25        | [`…ell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41)             |
| `GLCI-BUILTIN-SHELL-SAFE-03`  | User input is sanitised                              | scenario | CICD-SEC-4, CICD-SEC-7             | A.8.28                | [`…ell-security.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L55)             |
| `GLCI-BUILTIN-SHELL-SAFE-04`  | Hardcoded secrets are not present                    | scenario | CICD-SEC-6                         | A.8.28, A.5.16        | [`…ell-security.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L69)             |
| `GLCI-BUILTIN-SHELL-SAFE-05`  | chmod 777 is not used                                | scenario | CICD-SEC-7                         | A.8.28, A.8.9         | [`…ell-security.feature:83`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L83)             |

## Baseline job controls

**File:** [`baseline-jobs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature)
**Feature ID:** `GLCI-BUILTIN-BASELINE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-7
**ISO 27001:** A.8.25, A.8.9

Core job image and execution rules bundled with gitlab-compliance.

### Scenarios

| ID                         | Title                                  | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                               |
| -------------------------- | -------------------------------------- | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-BASELINE-01` | Job images must not use the latest tag | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9 |             | [`baseline-jobs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L26) |
| `GLCI-BUILTIN-BASELINE-02` | Non-template jobs must define rules    | HIGH     | CICD-SEC-1, CICD-SEC-7 | A.8.9, A.8.32 |             | [`baseline-jobs.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L42) |

## Component input constraints

**File:** [`component-inputs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature)
**Feature ID:** `GLCI-BUILTIN-COMPONENT`
**OWASP CI/CD:** CICD-SEC-7, CICD-SEC-8
**ISO 27001:** A.8.9, A.8.25

Advanced Scenario Outline for component inputs and conditional fields.

### Scenarios

| ID                          | Title                                            | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                                     |
| --------------------------- | ------------------------------------------------ | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-COMPONENT-01` | Component input mode constrains dependent fields | MEDIUM   | CICD-SEC-7, CICD-SEC-8 | A.8.9, A.8.25 |             | [`component-inputs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L26) |

## Include pinning essentials

**File:** [`include-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-INCPIN`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9, A.5.19

Baseline checks for component and fragment version pinning.

### Scenarios

| ID                       | Title                                      | Severity | OWASP CI/CD            | ISO 27001             | Description | Location                                                                                                                                                   |
| ------------------------ | ------------------------------------------ | -------- | ---------------------- | --------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCPIN-01` | Component includes must not track a branch | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 |             | [`include-pinning.feature:28`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L28) |
| `GLCI-BUILTIN-INCPIN-02` | Component includes must use semver         | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 |             | [`include-pinning.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L44) |

## Pipeline variable allowlist

**File:** [`variable-allowlist.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature)
**Feature ID:** `GLCI-BUILTIN-VARIABLES`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.9

Advanced Scenario Outline for required variables and allowed values.

### Scenarios

| ID                          | Title                                          | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                         |
| --------------------------- | ---------------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-VARIABLES-01` | Pipeline variables must match allowed patterns | MEDIUM   | CICD-SEC-7  | A.8.9     |             | [`variable-allowlist.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L22) |

## Container images must be pinned

**File:** [`supply-chain/image-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-IMAGE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Job images must use sha256 digests instead of mutable tags.

### Scenarios

| ID                      | Title                                                | Severity | OWASP CI/CD            | ISO 27001            | Description                                                         | Location                                                                                                                                                                         |
| ----------------------- | ---------------------------------------------------- | -------- | ---------------------- | -------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-IMAGE-01` | Job images must use sha256 digest                    | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Immutable digest pinning is the default supply-chain control.       | [`supply-chain/image-pinning.feature:29`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L29) |
| `GLCI-BUILTIN-IMAGE-02` | Disallow latest image tags                           | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Prevents jobs from using mutable latest tags such as docker:latest. | [`supply-chain/image-pinning.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L45) |
| `GLCI-BUILTIN-IMAGE-03` | Recommend explicit image version or digest           | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Ensures every job image includes a version tag or sha256 digest.    | [`supply-chain/image-pinning.feature:62`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L62) |
| `GLCI-BUILTIN-IMAGE-04` | Container images must not lag behind registry latest | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.8, A.8.9 | API-backed check against external registry tags.                    | [`supply-chain/image-pinning.feature:80`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L80) |

## Include versions must be semver-pinned

**File:** [`supply-chain/include-versions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature)
**Feature ID:** `GLCI-BUILTIN-INCLUDE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-8, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9, A.5.19

Project and component includes must pin immutable semver refs.

### Scenarios

| ID                        | Title                                                | Severity | OWASP CI/CD                        | ISO 27001             | Description                                                          | Location                                                                                                                                                                                 |
| ------------------------- | ---------------------------------------------------- | -------- | ---------------------------------- | --------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCLUDE-01` | Project includes must use valid semver               | HIGH     | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | Shared fragment refs must be semver tags, not branch names.          | [`supply-chain/include-versions.feature:30`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L30)   |
| `GLCI-BUILTIN-INCLUDE-02` | Component includes must use valid semver             | HIGH     | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | CI/CD components must pin explicit semver versions.                  | [`supply-chain/include-versions.feature:48`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L48)   |
| `GLCI-BUILTIN-INCLUDE-03` | Includes must track the latest release               | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | API-backed check that semver refs are not behind the newest tag.     | [`supply-chain/include-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)   |
| `GLCI-BUILTIN-INCLUDE-04` | New releases get a 30-day adoption window            | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Supply chain grace period before requiring upgrade to latest semver. | [`supply-chain/include-versions.feature:82`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L82)   |
| `GLCI-BUILTIN-INCLUDE-05` | Includes must stay within 90 days of upstream        | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Pinned refs must not trail latest by more than 90 days.              | [`supply-chain/include-versions.feature:99`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L99)   |
| `GLCI-BUILTIN-INCLUDE-06` | Includes must be within the latest three semver tags | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Pinned refs must rank among the N most recent semver releases.       | [`supply-chain/include-versions.feature:116`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L116) |

## Service containers must be version-pinned

**File:** [`supply-chain/service-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SERVICE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Service images such as docker:dind must include an explicit version.

### Scenarios

| ID                        | Title                              | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                                                             |
| ------------------------- | ---------------------------------- | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SERVICE-01` | docker:dind must include a version | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9 |             | [`supply-chain/service-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L26) |

## GitLab CI script conventions

**File:** [`shell/shell-ci-conventions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-CI`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.25, A.8.28

CI-specific hygiene for curl and deprecated variables.

### Scenarios

| ID                         | Title                                      | Severity | OWASP CI/CD | ISO 27001     | Description | Location                                                                                                                                                                         |
| -------------------------- | ------------------------------------------ | -------- | ----------- | ------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-CI-01` | curl uses fail flag                        | MEDIUM   | CICD-SEC-7  | A.8.28        |             | [`shell/shell-ci-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23) |
| `GLCI-BUILTIN-SHELL-CI-02` | Deprecated CI_BUILD variables are not used | MEDIUM   | CICD-SEC-7  | A.8.9, A.8.25 |             | [`shell/shell-ci-conventions.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L37) |
| `GLCI-BUILTIN-SHELL-CI-03` | CI variables should be quoted              | MEDIUM   | CICD-SEC-7  | A.8.28        |             | [`shell/shell-ci-conventions.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L50) |

## Command substitution

**File:** [`shell/shell-command-substitution.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SUB`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Prefer modern dollar-parentheses substitution over backticks.

### Scenarios

| ID                          | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                                     |
| --------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SUB-01` | Legacy backticks are not used           | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-command-substitution.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L22) |
| `GLCI-BUILTIN-SHELL-SUB-02` | Nested command substitution is readable | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-command-substitution.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L35) |

## Conditional expressions

**File:** [`shell/shell-conditionals.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-TEST`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Portable and safely quoted test expressions.

### Scenarios

| ID                           | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                     |
| ---------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-TEST-01` | Test operators are portable             | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-conditionals.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L22) |
| `GLCI-BUILTIN-SHELL-TEST-02` | Variables are quoted in test statements | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-conditionals.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L35) |

## Error handling

**File:** [`shell/shell-error-handling.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-ERR`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Strict mode and exit-code handling for GitLab CI job scripts.

### Scenarios

| ID                          | Title                                 | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                         |
| --------------------------- | ------------------------------------- | -------- | ----------- | --------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-ERR-01` | Scripts use strict mode               | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L23) |
| `GLCI-BUILTIN-SHELL-ERR-02` | Commands return meaningful exit codes | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L37) |
| `GLCI-BUILTIN-SHELL-ERR-03` | Functions propagate failures          | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L50) |

## Safe file operations

**File:** [`shell/shell-file-operations.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-FILE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Quoted paths, secure temps, and protected recursive rm.

### Scenarios

| ID                           | Title                                 | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                           |
| ---------------------------- | ------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-FILE-01` | File paths are quoted                 | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L22) |
| `GLCI-BUILTIN-SHELL-FILE-02` | Temporary files are securely created  | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L35) |
| `GLCI-BUILTIN-SHELL-FILE-03` | Dangerous rm operations are protected | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L49) |

## CI script dependency pinning

**File:** [`shell/shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIN`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Supply-chain pinning controls for packages and downloads in CI scripts.

### Scenarios

| ID                          | Title                                      | Severity | OWASP CI/CD            | ISO 27001      | Description                                                             | Location                                                                                                                                                             |
| --------------------------- | ------------------------------------------ | -------- | ---------------------- | -------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PIN-01` | Downloads must verify checksums            | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L26)   |
| `GLCI-BUILTIN-SHELL-PIN-02` | Disallow remote pipe to shell              | HIGH     | CICD-SEC-3, CICD-SEC-4 | A.8.28, A.8.25 |                                                                         | [`shell/shell-pinning.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L41)   |
| `GLCI-BUILTIN-SHELL-PIN-03` | pip packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Applies to both pip and pip3 install commands in job scripts.           | [`shell/shell-pinning.feature:57`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L57)   |
| `GLCI-BUILTIN-SHELL-PIN-04` | apk packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:72`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L72)   |
| `GLCI-BUILTIN-SHELL-PIN-05` | apt packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:87`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L87)   |
| `GLCI-BUILTIN-SHELL-PIN-06` | npm global packages must be version-pinned | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:102`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L102) |
| `GLCI-BUILTIN-SHELL-PIN-07` | go install must pin versions               | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:117`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L117) |
| `GLCI-BUILTIN-SHELL-PIN-08` | git clone must verify revision             | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:132`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L132) |
| `GLCI-BUILTIN-SHELL-PIN-09` | docker run and pull must pin images        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Script docker commands must reference an explicit tag or sha256 digest. | [`shell/shell-pinning.feature:148`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L148) |
| `GLCI-BUILTIN-SHELL-PIN-10` | yum/dnf packages must be version-pinned    | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Applies to yum, dnf, and microdnf install commands in job scripts.      | [`shell/shell-pinning.feature:164`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L164) |

## Pipeline safety

**File:** [`shell/shell-pipelines.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIPE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Detect pipeline failures with pipefail.

### Scenarios

| ID                           | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                               |
| ---------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PIPE-01` | Pipeline failures are detected          | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-pipelines.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L22) |
| `GLCI-BUILTIN-SHELL-PIPE-02` | Exit codes are checked across pipelines | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-pipelines.feature:36`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L36) |

## Shell portability

**File:** [`shell/shell-portability.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PORT`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Shebang validity and bash versus POSIX compatibility.

### Scenarios

| ID                           | Title                                    | Severity | OWASP CI/CD | ISO 27001      | Description | Location                                                                                                                                                                   |
| ---------------------------- | ---------------------------------------- | -------- | ----------- | -------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PORT-01` | Shebang is valid when present            | MEDIUM   | CICD-SEC-7  | A.8.28         |             | [`shell/shell-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23) |
| `GLCI-BUILTIN-SHELL-PORT-02` | Bash specific features are declared      | MEDIUM   | CICD-SEC-7  | A.8.28, A.8.25 |             | [`shell/shell-portability.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L37) |
| `GLCI-BUILTIN-SHELL-PORT-03` | POSIX compatibility is maintained for sh | MEDIUM   | CICD-SEC-7  | A.8.28, A.8.25 |             | [`shell/shell-portability.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L51) |

## Safe variable expansion

**File:** [`shell/shell-quoting.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-QUOTE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

ShellCheck-inspired quoting controls for GitLab CI job scripts.

### Scenarios

| ID                            | Title                              | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                           |
| ----------------------------- | ---------------------------------- | -------- | ----------- | --------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L23) |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L37) |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted   | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L51) |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly      | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L65) |

## Script reference resolution

**File:** [`shell/shell-references.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-REF`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.9, A.8.25

Detect unresolved GitLab !reference tags in script blocks.

### Scenarios

| ID                          | Title                           | Severity | OWASP CI/CD | ISO 27001     | Description | Location                                                                                                                                                                 |
| --------------------------- | ------------------------------- | -------- | ----------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-REF-01` | No unresolved script references | HIGH     | CICD-SEC-7  | A.8.9, A.8.25 |             | [`shell/shell-references.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L24) |

## Shell script security

**File:** [`shell/shell-security.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SAFE`
**OWASP CI/CD:** CICD-SEC-4, CICD-SEC-6, CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Prevent eval, remote pipe execution, secrets, and unsafe modes.

### Scenarios

| ID                           | Title                             | Severity | OWASP CI/CD            | ISO 27001      | Description | Location                                                                                                                                                             |
| ---------------------------- | --------------------------------- | -------- | ---------------------- | -------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SAFE-01` | Eval is not used                  | HIGH     | CICD-SEC-4, CICD-SEC-7 | A.8.28         |             | [`shell/shell-security.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L26) |
| `GLCI-BUILTIN-SHELL-SAFE-02` | Untrusted input is not executed   | HIGH     | CICD-SEC-3, CICD-SEC-4 | A.8.28, A.8.25 |             | [`shell/shell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41) |
| `GLCI-BUILTIN-SHELL-SAFE-03` | User input is sanitised           | HIGH     | CICD-SEC-4, CICD-SEC-7 | A.8.28         |             | [`shell/shell-security.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L55) |
| `GLCI-BUILTIN-SHELL-SAFE-04` | Hardcoded secrets are not present | HIGH     | CICD-SEC-6             | A.8.28, A.5.16 |             | [`shell/shell-security.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L69) |
| `GLCI-BUILTIN-SHELL-SAFE-05` | chmod 777 is not used             | MEDIUM   | CICD-SEC-7             | A.8.28, A.8.9  |             | [`shell/shell-security.feature:83`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L83) |
# GitLab CI Compliance Policy Catalog

- **Policies directory:** `src/compliance/builtin_policies`
- **Generated:** 2026-07-30 21:27:41 UTC

## Index

| ID                            | Title                                                | Scope    | OWASP CI/CD                        | ISO 27001             | Location                                                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------- | -------- | ---------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-BASELINE`       | Baseline job controls                                | feature  | CICD-SEC-3, CICD-SEC-7             | A.8.25, A.8.9         | [`baseline-jobs.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L13)                    |
| `GLCI-BUILTIN-BASELINE-01`    | Job images must not use the latest tag               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`baseline-jobs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L26)                    |
| `GLCI-BUILTIN-BASELINE-02`    | Non-template jobs must define rules                  | scenario | CICD-SEC-1, CICD-SEC-7             | A.8.9, A.8.32         | [`baseline-jobs.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L42)                    |
| `GLCI-BUILTIN-COMPONENT`      | Component input constraints                          | feature  | CICD-SEC-7, CICD-SEC-8             | A.8.9, A.8.25         | [`…onent-inputs.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L13)                 |
| `GLCI-BUILTIN-COMPONENT-01`   | Component input mode constrains dependent fields     | scenario | CICD-SEC-7, CICD-SEC-8             | A.8.9, A.8.25         | [`…onent-inputs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L26)                 |
| `GLCI-BUILTIN-INCPIN`         | Include pinning essentials                           | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L14)                  |
| `GLCI-BUILTIN-INCPIN-01`      | Component includes must not track a branch           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:28`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L28)                  |
| `GLCI-BUILTIN-INCPIN-02`      | Component includes must use semver                   | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…lude-pinning.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L44)                  |
| `GLCI-BUILTIN-VARIABLES`      | Pipeline variable allowlist                          | feature  | CICD-SEC-7                         | A.8.9                 | [`…le-allowlist.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L11)               |
| `GLCI-BUILTIN-VARIABLES-01`   | Pipeline variables must match allowed patterns       | scenario | CICD-SEC-7                         | A.8.9                 | [`…le-allowlist.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L22)               |
| `GLCI-BUILTIN-IMAGE`          | Container images must be pinned                      | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L15)       |
| `GLCI-BUILTIN-IMAGE-01`       | Job images must use sha256 digest                    | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:29`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L29)       |
| `GLCI-BUILTIN-IMAGE-02`       | Disallow latest image tags                           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L45)       |
| `GLCI-BUILTIN-IMAGE-03`       | Recommend explicit image version or digest           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…mage-pinning.feature:62`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L62)       |
| `GLCI-BUILTIN-IMAGE-04`       | Container images must not lag behind registry latest | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…mage-pinning.feature:80`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L80)       |
| `GLCI-BUILTIN-INCLUDE`        | Include versions must be valid semver                | feature  | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:15`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L15)    |
| `GLCI-BUILTIN-INCLUDE-01`     | Project includes must use valid semver               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:30`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L30)    |
| `GLCI-BUILTIN-INCLUDE-02`     | Component includes must use valid semver             | scenario | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | [`…ude-versions.feature:48`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L48)    |
| `GLCI-BUILTIN-INCLUDE-03`     | Includes must track the latest release               | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)    |
| `GLCI-BUILTIN-INCLUDE-04`     | New releases get a 30-day adoption window            | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:82`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L82)    |
| `GLCI-BUILTIN-INCLUDE-05`     | Includes must stay within 90 days of upstream        | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…ude-versions.feature:99`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L99)    |
| `GLCI-BUILTIN-INCLUDE-06`     | Includes must be within the latest three semver tags | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | [`…de-versions.feature:116`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L116)   |
| `GLCI-BUILTIN-SERVICE`        | Service containers must be version-pinned            | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…vice-pinning.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L13)     |
| `GLCI-BUILTIN-SERVICE-01`     | docker:dind must include a version                   | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…vice-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L26)     |
| `GLCI-BUILTIN-SHELL-CI`       | GitLab CI script conventions                         | feature  | CICD-SEC-7                         | A.8.25, A.8.28        | [`…-conventions.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L12)       |
| `GLCI-BUILTIN-SHELL-CI-01`    | curl uses fail flag                                  | scenario | CICD-SEC-7                         | A.8.28                | [`…-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23)       |
| `GLCI-BUILTIN-SHELL-CI-02`    | Deprecated CI_BUILD variables are not used           | scenario | CICD-SEC-7                         | A.8.9, A.8.25         | [`…-conventions.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L37)       |
| `GLCI-BUILTIN-SHELL-CI-03`    | CI variables should be quoted                        | scenario | CICD-SEC-7                         | A.8.28                | [`…-conventions.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L50)       |
| `GLCI-BUILTIN-SHELL-SUB`      | Command substitution standards                       | feature  | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L11) |
| `GLCI-BUILTIN-SHELL-SUB-01`   | Legacy backticks are not used                        | scenario | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L22) |
| `GLCI-BUILTIN-SHELL-SUB-02`   | Nested command substitution is readable              | scenario | CICD-SEC-7                         | A.8.28                | [`…substitution.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L35) |
| `GLCI-BUILTIN-SHELL-TEST`     | Conditional expression standards                     | feature  | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L11)         |
| `GLCI-BUILTIN-SHELL-TEST-01`  | Test operators are portable                          | scenario | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L22)         |
| `GLCI-BUILTIN-SHELL-TEST-02`  | Variables are quoted in test statements              | scenario | CICD-SEC-7                         | A.8.28                | [`…conditionals.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L35)         |
| `GLCI-BUILTIN-SHELL-ERR`      | Error handling                                       | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…ror-handling.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L12)       |
| `GLCI-BUILTIN-SHELL-ERR-01`   | Scripts use strict mode                              | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L23)       |
| `GLCI-BUILTIN-SHELL-ERR-02`   | Commands return meaningful exit codes                | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L37)       |
| `GLCI-BUILTIN-SHELL-ERR-03`   | Functions propagate failures                         | scenario | CICD-SEC-7                         | A.8.28                | [`…ror-handling.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L50)       |
| `GLCI-BUILTIN-SHELL-FILE`     | Safe file operations                                 | feature  | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L11)      |
| `GLCI-BUILTIN-SHELL-FILE-01`  | File paths are quoted                                | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L22)      |
| `GLCI-BUILTIN-SHELL-FILE-02`  | Temporary files are securely created                 | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L35)      |
| `GLCI-BUILTIN-SHELL-FILE-03`  | Dangerous rm operations are protected                | scenario | CICD-SEC-7                         | A.8.28                | [`…e-operations.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L49)      |
| `GLCI-BUILTIN-SHELL-PIN`      | CI script dependency pinning                         | feature  | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:13`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L13)              |
| `GLCI-BUILTIN-SHELL-PIN-01`   | Downloads must verify checksums                      | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L26)              |
| `GLCI-BUILTIN-SHELL-PIN-02`   | Disallow remote pipe to shell                        | scenario | CICD-SEC-3, CICD-SEC-4             | A.8.28, A.8.25        | [`…hell-pinning.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L41)              |
| `GLCI-BUILTIN-SHELL-PIN-03`   | pip packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:57`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L57)              |
| `GLCI-BUILTIN-SHELL-PIN-04`   | apk packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:72`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L72)              |
| `GLCI-BUILTIN-SHELL-PIN-05`   | apt packages must be version-pinned                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…hell-pinning.feature:87`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L87)              |
| `GLCI-BUILTIN-SHELL-PIN-06`   | npm global packages must be version-pinned           | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:102`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L102)             |
| `GLCI-BUILTIN-SHELL-PIN-07`   | go install must pin versions                         | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:117`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L117)             |
| `GLCI-BUILTIN-SHELL-PIN-08`   | git clone must verify revision                       | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:132`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L132)             |
| `GLCI-BUILTIN-SHELL-PIN-09`   | docker run and pull must pin images                  | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:148`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L148)             |
| `GLCI-BUILTIN-SHELL-PIN-10`   | yum/dnf packages must be version-pinned              | scenario | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9         | [`…ell-pinning.feature:164`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L164)             |
| `GLCI-BUILTIN-SHELL-PIPE`     | Pipeline safety                                      | feature  | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:11`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L11)            |
| `GLCI-BUILTIN-SHELL-PIPE-01`  | Pipeline failures are detected                       | scenario | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L22)            |
| `GLCI-BUILTIN-SHELL-PIPE-02`  | Exit codes are checked across pipelines              | scenario | CICD-SEC-7                         | A.8.28                | [`…ll-pipelines.feature:36`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L36)            |
| `GLCI-BUILTIN-SHELL-PORT`     | Shell portability                                    | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L12)          |
| `GLCI-BUILTIN-SHELL-PORT-01`  | Shebang is valid when present                        | scenario | CICD-SEC-7                         | A.8.28                | [`…-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23)          |
| `GLCI-BUILTIN-SHELL-PORT-02`  | Bash specific features are declared                  | scenario | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L37)          |
| `GLCI-BUILTIN-SHELL-PORT-03`  | POSIX compatibility is maintained for sh             | scenario | CICD-SEC-7                         | A.8.28, A.8.25        | [`…-portability.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L51)          |
| `GLCI-BUILTIN-SHELL-QUOTE`    | Safe variable expansion                              | feature  | CICD-SEC-7                         | A.8.28, A.8.25        | [`…hell-quoting.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L12)              |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded                   | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L23)              |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted                   | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L37)              |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted                     | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L51)              |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly                        | scenario | CICD-SEC-7                         | A.8.28                | [`…hell-quoting.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L65)              |
| `GLCI-BUILTIN-SHELL-REF`      | Script reference resolution                          | feature  | CICD-SEC-7                         | A.8.9, A.8.25         | [`…l-references.feature:12`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L12)           |
| `GLCI-BUILTIN-SHELL-REF-01`   | No unresolved script references                      | scenario | CICD-SEC-7                         | A.8.9, A.8.25         | [`…l-references.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L24)           |
| `GLCI-BUILTIN-SHELL-SAFE`     | Shell script security                                | feature  | CICD-SEC-4, CICD-SEC-6, CICD-SEC-7 | A.8.28, A.8.25        | [`…ell-security.feature:14`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L14)             |
| `GLCI-BUILTIN-SHELL-SAFE-01`  | Eval is not used                                     | scenario | CICD-SEC-4, CICD-SEC-7             | A.8.28                | [`…ell-security.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L26)             |
| `GLCI-BUILTIN-SHELL-SAFE-02`  | Untrusted input is not executed                      | scenario | CICD-SEC-3, CICD-SEC-4             | A.8.28, A.8.25        | [`…ell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41)             |
| `GLCI-BUILTIN-SHELL-SAFE-03`  | User input is sanitised                              | scenario | CICD-SEC-4, CICD-SEC-7             | A.8.28                | [`…ell-security.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L55)             |
| `GLCI-BUILTIN-SHELL-SAFE-04`  | Hardcoded secrets are not present                    | scenario | CICD-SEC-6                         | A.8.28, A.5.16        | [`…ell-security.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L69)             |
| `GLCI-BUILTIN-SHELL-SAFE-05`  | chmod 777 is not used                                | scenario | CICD-SEC-7                         | A.8.28, A.8.9         | [`…ell-security.feature:83`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L83)             |

## Baseline job controls

**File:** [`baseline-jobs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature)
**Feature ID:** `GLCI-BUILTIN-BASELINE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-7
**ISO 27001:** A.8.25, A.8.9

Core job image and execution rules bundled with gitlab-compliance.

### Scenarios

| ID                         | Title                                  | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                               |
| -------------------------- | -------------------------------------- | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-BASELINE-01` | Job images must not use the latest tag | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9 |             | [`baseline-jobs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L26) |
| `GLCI-BUILTIN-BASELINE-02` | Non-template jobs must define rules    | HIGH     | CICD-SEC-1, CICD-SEC-7 | A.8.9, A.8.32 |             | [`baseline-jobs.feature:42`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/baseline-jobs.feature#L42) |

## Component input constraints

**File:** [`component-inputs.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature)
**Feature ID:** `GLCI-BUILTIN-COMPONENT`
**OWASP CI/CD:** CICD-SEC-7, CICD-SEC-8
**ISO 27001:** A.8.9, A.8.25

Advanced Scenario Outline for component inputs and conditional fields.

### Scenarios

| ID                          | Title                                            | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                                     |
| --------------------------- | ------------------------------------------------ | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-COMPONENT-01` | Component input mode constrains dependent fields | MEDIUM   | CICD-SEC-7, CICD-SEC-8 | A.8.9, A.8.25 |             | [`component-inputs.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/component-inputs.feature#L26) |

## Include pinning essentials

**File:** [`include-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-INCPIN`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9, A.5.19

Baseline checks for component and fragment version pinning.

### Scenarios

| ID                       | Title                                      | Severity | OWASP CI/CD            | ISO 27001             | Description | Location                                                                                                                                                   |
| ------------------------ | ------------------------------------------ | -------- | ---------------------- | --------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCPIN-01` | Component includes must not track a branch | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 |             | [`include-pinning.feature:28`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L28) |
| `GLCI-BUILTIN-INCPIN-02` | Component includes must use semver         | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 |             | [`include-pinning.feature:44`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/include-pinning.feature#L44) |

## Pipeline variable allowlist

**File:** [`variable-allowlist.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature)
**Feature ID:** `GLCI-BUILTIN-VARIABLES`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.9

Advanced Scenario Outline for required variables and allowed values.

### Scenarios

| ID                          | Title                                          | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                         |
| --------------------------- | ---------------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-VARIABLES-01` | Pipeline variables must match allowed patterns | MEDIUM   | CICD-SEC-7  | A.8.9     |             | [`variable-allowlist.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/variable-allowlist.feature#L22) |

## Container images must be pinned

**File:** [`supply-chain/image-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-IMAGE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Job images must use sha256 digests instead of mutable tags.

### Scenarios

| ID                      | Title                                                | Severity | OWASP CI/CD            | ISO 27001            | Description                                                         | Location                                                                                                                                                                         |
| ----------------------- | ---------------------------------------------------- | -------- | ---------------------- | -------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-IMAGE-01` | Job images must use sha256 digest                    | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Immutable digest pinning is the default supply-chain control.       | [`supply-chain/image-pinning.feature:29`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L29) |
| `GLCI-BUILTIN-IMAGE-02` | Disallow latest image tags                           | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Prevents jobs from using mutable latest tags such as docker:latest. | [`supply-chain/image-pinning.feature:45`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L45) |
| `GLCI-BUILTIN-IMAGE-03` | Recommend explicit image version or digest           | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9        | Ensures every job image includes a version tag or sha256 digest.    | [`supply-chain/image-pinning.feature:62`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L62) |
| `GLCI-BUILTIN-IMAGE-04` | Container images must not lag behind registry latest | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.8, A.8.9 | API-backed check against external registry tags.                    | [`supply-chain/image-pinning.feature:80`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/image-pinning.feature#L80) |

## Include versions must be semver-pinned

**File:** [`supply-chain/include-versions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature)
**Feature ID:** `GLCI-BUILTIN-INCLUDE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-8, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9, A.5.19

Project and component includes must pin immutable semver refs.

### Scenarios

| ID                        | Title                                                | Severity | OWASP CI/CD                        | ISO 27001             | Description                                                          | Location                                                                                                                                                                                 |
| ------------------------- | ---------------------------------------------------- | -------- | ---------------------------------- | --------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-INCLUDE-01` | Project includes must use valid semver               | HIGH     | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.9, A.5.19 | Shared fragment refs must be semver tags, not branch names.          | [`supply-chain/include-versions.feature:30`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L30)   |
| `GLCI-BUILTIN-INCLUDE-02` | Component includes must use valid semver             | HIGH     | CICD-SEC-3, CICD-SEC-8, CICD-SEC-9 | A.8.25, A.8.9, A.5.19 | CI/CD components must pin explicit semver versions.                  | [`supply-chain/include-versions.feature:48`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L48)   |
| `GLCI-BUILTIN-INCLUDE-03` | Includes must track the latest release               | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | API-backed check that semver refs are not behind the newest tag.     | [`supply-chain/include-versions.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L65)   |
| `GLCI-BUILTIN-INCLUDE-04` | New releases get a 30-day adoption window            | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Supply chain grace period before requiring upgrade to latest semver. | [`supply-chain/include-versions.feature:82`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L82)   |
| `GLCI-BUILTIN-INCLUDE-05` | Includes must stay within 90 days of upstream        | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Pinned refs must not trail latest by more than 90 days.              | [`supply-chain/include-versions.feature:99`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L99)   |
| `GLCI-BUILTIN-INCLUDE-06` | Includes must be within the latest three semver tags | MEDIUM   | CICD-SEC-3, CICD-SEC-9             | A.8.25, A.8.8, A.8.9  | Pinned refs must rank among the N most recent semver releases.       | [`supply-chain/include-versions.feature:116`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/include-versions.feature#L116) |

## Service containers must be version-pinned

**File:** [`supply-chain/service-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SERVICE`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Service images such as docker:dind must include an explicit version.

### Scenarios

| ID                        | Title                              | Severity | OWASP CI/CD            | ISO 27001     | Description | Location                                                                                                                                                                             |
| ------------------------- | ---------------------------------- | -------- | ---------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SERVICE-01` | docker:dind must include a version | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9 |             | [`supply-chain/service-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/supply-chain/service-pinning.feature#L26) |

## GitLab CI script conventions

**File:** [`shell/shell-ci-conventions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-CI`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.25, A.8.28

CI-specific hygiene for curl and deprecated variables.

### Scenarios

| ID                         | Title                                      | Severity | OWASP CI/CD | ISO 27001     | Description | Location                                                                                                                                                                         |
| -------------------------- | ------------------------------------------ | -------- | ----------- | ------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-CI-01` | curl uses fail flag                        | MEDIUM   | CICD-SEC-7  | A.8.28        |             | [`shell/shell-ci-conventions.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L23) |
| `GLCI-BUILTIN-SHELL-CI-02` | Deprecated CI_BUILD variables are not used | MEDIUM   | CICD-SEC-7  | A.8.9, A.8.25 |             | [`shell/shell-ci-conventions.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L37) |
| `GLCI-BUILTIN-SHELL-CI-03` | CI variables should be quoted              | MEDIUM   | CICD-SEC-7  | A.8.28        |             | [`shell/shell-ci-conventions.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-ci-conventions.feature#L50) |

## Command substitution

**File:** [`shell/shell-command-substitution.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SUB`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Prefer modern dollar-parentheses substitution over backticks.

### Scenarios

| ID                          | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                                     |
| --------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SUB-01` | Legacy backticks are not used           | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-command-substitution.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L22) |
| `GLCI-BUILTIN-SHELL-SUB-02` | Nested command substitution is readable | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-command-substitution.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-command-substitution.feature#L35) |

## Conditional expressions

**File:** [`shell/shell-conditionals.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-TEST`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Portable and safely quoted test expressions.

### Scenarios

| ID                           | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                     |
| ---------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-TEST-01` | Test operators are portable             | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-conditionals.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L22) |
| `GLCI-BUILTIN-SHELL-TEST-02` | Variables are quoted in test statements | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-conditionals.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-conditionals.feature#L35) |

## Error handling

**File:** [`shell/shell-error-handling.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-ERR`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Strict mode and exit-code handling for GitLab CI job scripts.

### Scenarios

| ID                          | Title                                 | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                         |
| --------------------------- | ------------------------------------- | -------- | ----------- | --------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-ERR-01` | Scripts use strict mode               | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L23) |
| `GLCI-BUILTIN-SHELL-ERR-02` | Commands return meaningful exit codes | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L37) |
| `GLCI-BUILTIN-SHELL-ERR-03` | Functions propagate failures          | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-error-handling.feature:50`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-error-handling.feature#L50) |

## Safe file operations

**File:** [`shell/shell-file-operations.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-FILE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Quoted paths, secure temps, and protected recursive rm.

### Scenarios

| ID                           | Title                                 | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                                           |
| ---------------------------- | ------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-FILE-01` | File paths are quoted                 | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L22) |
| `GLCI-BUILTIN-SHELL-FILE-02` | Temporary files are securely created  | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:35`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L35) |
| `GLCI-BUILTIN-SHELL-FILE-03` | Dangerous rm operations are protected | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-file-operations.feature:49`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-file-operations.feature#L49) |

## CI script dependency pinning

**File:** [`shell/shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIN`
**OWASP CI/CD:** CICD-SEC-3, CICD-SEC-9
**ISO 27001:** A.8.25, A.8.9

Supply-chain pinning controls for packages and downloads in CI scripts.

### Scenarios

| ID                          | Title                                      | Severity | OWASP CI/CD            | ISO 27001      | Description                                                             | Location                                                                                                                                                             |
| --------------------------- | ------------------------------------------ | -------- | ---------------------- | -------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PIN-01` | Downloads must verify checksums            | HIGH     | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L26)   |
| `GLCI-BUILTIN-SHELL-PIN-02` | Disallow remote pipe to shell              | HIGH     | CICD-SEC-3, CICD-SEC-4 | A.8.28, A.8.25 |                                                                         | [`shell/shell-pinning.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L41)   |
| `GLCI-BUILTIN-SHELL-PIN-03` | pip packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Applies to both pip and pip3 install commands in job scripts.           | [`shell/shell-pinning.feature:57`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L57)   |
| `GLCI-BUILTIN-SHELL-PIN-04` | apk packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:72`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L72)   |
| `GLCI-BUILTIN-SHELL-PIN-05` | apt packages must be version-pinned        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:87`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L87)   |
| `GLCI-BUILTIN-SHELL-PIN-06` | npm global packages must be version-pinned | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:102`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L102) |
| `GLCI-BUILTIN-SHELL-PIN-07` | go install must pin versions               | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:117`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L117) |
| `GLCI-BUILTIN-SHELL-PIN-08` | git clone must verify revision             | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  |                                                                         | [`shell/shell-pinning.feature:132`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L132) |
| `GLCI-BUILTIN-SHELL-PIN-09` | docker run and pull must pin images        | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Script docker commands must reference an explicit tag or sha256 digest. | [`shell/shell-pinning.feature:148`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L148) |
| `GLCI-BUILTIN-SHELL-PIN-10` | yum/dnf packages must be version-pinned    | MEDIUM   | CICD-SEC-3, CICD-SEC-9 | A.8.25, A.8.9  | Applies to yum, dnf, and microdnf install commands in job scripts.      | [`shell/shell-pinning.feature:164`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature#L164) |

## Pipeline safety

**File:** [`shell/shell-pipelines.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PIPE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28

Detect pipeline failures with pipefail.

### Scenarios

| ID                           | Title                                   | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                               |
| ---------------------------- | --------------------------------------- | -------- | ----------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PIPE-01` | Pipeline failures are detected          | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-pipelines.feature:22`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L22) |
| `GLCI-BUILTIN-SHELL-PIPE-02` | Exit codes are checked across pipelines | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-pipelines.feature:36`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pipelines.feature#L36) |

## Shell portability

**File:** [`shell/shell-portability.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-PORT`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Shebang validity and bash versus POSIX compatibility.

### Scenarios

| ID                           | Title                                    | Severity | OWASP CI/CD | ISO 27001      | Description | Location                                                                                                                                                                   |
| ---------------------------- | ---------------------------------------- | -------- | ----------- | -------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-PORT-01` | Shebang is valid when present            | MEDIUM   | CICD-SEC-7  | A.8.28         |             | [`shell/shell-portability.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L23) |
| `GLCI-BUILTIN-SHELL-PORT-02` | Bash specific features are declared      | MEDIUM   | CICD-SEC-7  | A.8.28, A.8.25 |             | [`shell/shell-portability.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L37) |
| `GLCI-BUILTIN-SHELL-PORT-03` | POSIX compatibility is maintained for sh | MEDIUM   | CICD-SEC-7  | A.8.28, A.8.25 |             | [`shell/shell-portability.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-portability.feature#L51) |

## Safe variable expansion

**File:** [`shell/shell-quoting.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-QUOTE`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

ShellCheck-inspired quoting controls for GitLab CI job scripts.

### Scenarios

| ID                            | Title                              | Severity | OWASP CI/CD | ISO 27001 | Description | Location                                                                                                                                                           |
| ----------------------------- | ---------------------------------- | -------- | ----------- | --------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-QUOTE-01` | Variables are quoted when expanded | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:23`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L23) |
| `GLCI-BUILTIN-SHELL-QUOTE-02` | Variables used in paths are quoted | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:37`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L37) |
| `GLCI-BUILTIN-SHELL-QUOTE-03` | Command substitutions are quoted   | HIGH     | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:51`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L51) |
| `GLCI-BUILTIN-SHELL-QUOTE-04` | Arrays are expanded correctly      | MEDIUM   | CICD-SEC-7  | A.8.28    |             | [`shell/shell-quoting.feature:65`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-quoting.feature#L65) |

## Script reference resolution

**File:** [`shell/shell-references.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-REF`
**OWASP CI/CD:** CICD-SEC-7
**ISO 27001:** A.8.9, A.8.25

Detect unresolved GitLab !reference tags in script blocks.

### Scenarios

| ID                          | Title                           | Severity | OWASP CI/CD | ISO 27001     | Description | Location                                                                                                                                                                 |
| --------------------------- | ------------------------------- | -------- | ----------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GLCI-BUILTIN-SHELL-REF-01` | No unresolved script references | HIGH     | CICD-SEC-7  | A.8.9, A.8.25 |             | [`shell/shell-references.feature:24`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-references.feature#L24) |

## Shell script security

**File:** [`shell/shell-security.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature)
**Feature ID:** `GLCI-BUILTIN-SHELL-SAFE`
**OWASP CI/CD:** CICD-SEC-4, CICD-SEC-6, CICD-SEC-7
**ISO 27001:** A.8.28, A.8.25

Prevent eval, remote pipe execution, secrets, and unsafe modes.

### Scenarios

| ID                           | Title                             | Severity | OWASP CI/CD            | ISO 27001      | Description | Location                                                                                                                                                             |
| ---------------------------- | --------------------------------- | -------- | ---------------------- | -------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GLCI-BUILTIN-SHELL-SAFE-01` | Eval is not used                  | HIGH     | CICD-SEC-4, CICD-SEC-7 | A.8.28         |             | [`shell/shell-security.feature:26`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L26) |
| `GLCI-BUILTIN-SHELL-SAFE-02` | Untrusted input is not executed   | HIGH     | CICD-SEC-3, CICD-SEC-4 | A.8.28, A.8.25 |             | [`shell/shell-security.feature:41`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L41) |
| `GLCI-BUILTIN-SHELL-SAFE-03` | User input is sanitised           | HIGH     | CICD-SEC-4, CICD-SEC-7 | A.8.28         |             | [`shell/shell-security.feature:55`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L55) |
| `GLCI-BUILTIN-SHELL-SAFE-04` | Hardcoded secrets are not present | HIGH     | CICD-SEC-6             | A.8.28, A.5.16 |             | [`shell/shell-security.feature:69`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L69) |
| `GLCI-BUILTIN-SHELL-SAFE-05` | chmod 777 is not used             | MEDIUM   | CICD-SEC-7             | A.8.28, A.8.9  |             | [`shell/shell-security.feature:83`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-security.feature#L83) |
