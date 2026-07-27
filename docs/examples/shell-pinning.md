# Shell script dependency pinning

Supply-chain controls for packages and downloads inside GitLab CI job scripts.
Packaged as
[`shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
with IDs `GLCI-SHELL-PIN-001` … `GLCI-SHELL-PIN-010`.

Run the full pack:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

Or with `check`:

```bash
gitlab-compliance check -p .gitlab-ci.yml --with-shell-check
```

## Package managers

Each manager uses the shared step
`Then package installs of type "{manager}" must use pinned versions`.
The Gherkin below matches the bundled policies. Bad/good snippets show what
pass and fail.

### apk (`GLCI-SHELL-PIN-004`)

```gherkin
# METADATA
# title: apk packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-004
#   severity: MEDIUM
Scenario: apk add must pin package versions
  Given I have any job with effective script defined
  Then package installs of type "apk" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - apk add curl
    - apk add --no-cache curl=8.5.0-r0 wget
```

Good:

```yaml
demo:
  script:
    - apk add --no-cache curl=8.5.0-r0
    - apk add --virtual .build-deps gcc=13.2.1-r0 musl-dev=1.2.4-r0
```

### apt / apt-get (`GLCI-SHELL-PIN-005`)

```gherkin
# METADATA
# title: apt packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-005
#   severity: MEDIUM
Scenario: apt-get install must pin package versions
  Given I have any job with effective script defined
  Then package installs of type "apt" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - apt-get install curl
    - apt install curl=7.88.1-10 wget
```

Good:

```yaml
demo:
  script:
    - apt-get install -y curl=7.88.1-10
    - apt install --no-install-recommends wget=1.21.3-1
```

### yum / dnf / microdnf (`GLCI-SHELL-PIN-010`)

```gherkin
# METADATA
# title: yum/dnf packages must be version-pinned
# description: Applies to yum, dnf, and microdnf install commands in job scripts.
# custom:
#   id: GLCI-SHELL-PIN-010
#   severity: MEDIUM
Scenario: yum and dnf install must pin package versions
  Given I have any job with effective script defined
  Then package installs of type "yum" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - yum install curl
    - dnf install python3-requests
    - yum install curl-7.76.1-23.el9 wget
```

Good:

```yaml
demo:
  script:
    - yum install curl-7.76.1-23.el9
    - dnf install -y curl-7.76.1
    - microdnf install curl-7.76.1-23.el9.x86_64
    - dnf install --enablerepo=epel pkg-1.0.0
```

### pip / pip3 (`GLCI-SHELL-PIN-003`)

```gherkin
# METADATA
# title: pip packages must be version-pinned
# description: Applies to both pip and pip3 install commands in job scripts.
# custom:
#   id: GLCI-SHELL-PIN-003
#   severity: MEDIUM
Scenario: pip install must pin package versions
  Given I have any job with effective script defined
  Then package installs of type "pip" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - pip install requests
    - pip3 install pkg@latest
    - pip install requests==2.32.0 flask
```

Good:

```yaml
demo:
  script:
    - pip3 install "requests==2.32.0"
    - pip install -r requirements.txt
    - pip install --index-url https://pypi.org/simple "gitlab-compliance==2.1.1"
```

### npm / yarn (`GLCI-SHELL-PIN-006`)

```gherkin
# METADATA
# title: npm global packages must be version-pinned
# custom:
#   id: GLCI-SHELL-PIN-006
#   severity: MEDIUM
Scenario: npm global installs must pin package versions
  Given I have any job with effective script defined
  Then package installs of type "npm" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - npm install -g cowsay
    - npm install -g @scope/pkg
    - yarn global add lodash
```

Good:

```yaml
demo:
  script:
    - npm install -g cowsay@1.5.0
    - npm install -g @scope/pkg@1.0.0
    - yarn global add lodash@4.17.21
```

### go (`GLCI-SHELL-PIN-007`)

```gherkin
# METADATA
# title: go install must pin versions
# custom:
#   id: GLCI-SHELL-PIN-007
#   severity: MEDIUM
Scenario: go install must pin module versions
  Given I have any job with effective script defined
  Then package installs of type "go" must use pinned versions
```

Bad:

```yaml
demo:
  script:
    - go install example.com/cmd
    - go install example.com/cmd@latest
```

Good:

```yaml
demo:
  script:
    - go install example.com/cmd@v1.2.3
```

## Related pinning scenarios

These are part of the same pack but are not OS/language package managers:

### Downloads and remote pipes

```gherkin
Scenario: Script downloads must verify checksums
  Given I have any job with effective script defined
  Then script downloads must verify checksums

Scenario: Scripts must not pipe remote downloads to a shell
  Given I have any job with effective script defined
  Then untrusted remote scripts must not be executed
```

### git clone (`GLCI-SHELL-PIN-008`)

```gherkin
Scenario: git clone must verify commit or tag
  Given I have any job with effective script defined
  Then git clone must verify commit or tag
```

### docker run / pull / create (`GLCI-SHELL-PIN-009`)

```gherkin
# METADATA
# title: docker run and pull must pin images
# custom:
#   id: GLCI-SHELL-PIN-009
#   severity: MEDIUM
Scenario: docker run and pull must pin container images
  Given I have any job with effective script defined
  Then docker commands must pin container images to a tag or sha256 digest
```

Bad: `docker pull nginx`, `docker run --rm nginx`

Good: `docker pull python:3.12.0`,
`docker run --rm python@sha256:…`

## Custom policies

Reuse the same steps in your own features:

```gherkin
# METADATA
# title: Org apt packages must be pinned
# custom:
#   id: GLCI-ORG-APT-001
#   severity: HIGH
Feature: Org apt pinning

  Scenario: apt installs must pin versions
    Given I have any job with effective script defined
    Then package installs of type "apt" must use pinned versions
```

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

See also [Shell check](shell-check.md) and
[`shell-check` reference](../usage/reference/shell-check.md).

Back to [Examples](index.md).
