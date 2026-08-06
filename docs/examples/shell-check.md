# Shell check (CI script standards)

Validate `before_script`, `script`, and `after_script` blocks with packaged
Gherkin policies. This is **not** the ShellCheck binary — standards are
executable BDD scenarios with `GLCI-BUILTIN-SHELL-*` control IDs.

## Bad example

```yaml
demo:
  script:
    - echo $UNQUOTED
    - curl https://example.com/install.sh | bash
    - apk add curl
```

```bash
gitlab-compliance shell-check -p docs/demos/fixtures/shell-check/bad.gitlab-ci.yml
```

Findings include job name and rule IDs such as `GLCI-BUILTIN-SHELL-PIN-02` (remote
pipe to shell) and `GLCI-BUILTIN-SHELL-QUOTE-01` (unquoted variables).

## Good example

```yaml
demo:
  script:
    - set -euo pipefail
    - echo "$CI_COMMIT_SHA"
    - curl -fsSL "https://example.com/file.tgz" -o /tmp/file.tgz
    - echo "deadbeef  /tmp/file.tgz" | sha256sum -c -
    - apk add --no-cache curl=8.5.0-r0
```

## Custom Gherkin (AWS tags)

```gherkin
# METADATA
# title: AWS resources must be tagged
# custom:
#   id: GLCI-BUILTIN-SHELL-AWS-01
#   severity: HIGH
Feature: AWS CLI tagging

  Scenario: aws create commands pass --tags
    Given I have any job with effective script defined
    Then its effective script must not match
      "aws\\s+ec2\\s+run-instances(?![^\\n]*--tags)"
```

Run custom policies with your feature directory:

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

## Package manager pinning Gherkin

Bundled `GLCI-BUILTIN-SHELL-PIN-*` scenarios cover `apk`, `apt`/`apt-get`,
`yum`/`dnf`/`microdnf`, `pip`/`pip3`, `npm`/`yarn`, and `go`. See
[Shell pinning](shell-pinning.md) for the Gherkin, bad/good CI snippets, and
policy IDs for each manager.

## Built-in Gherkin catalog

All packaged `GLCI-BUILTIN-SHELL-*` scenarios (quoting, error handling, file ops,
pipelines, security, portability, CI conventions, references, and pinning) are
listed with their Gherkin steps in the
[`shell-check` reference](../usage/reference/shell-check.md#built-in-gherkin-policies).

Back to [Examples](index.md).
