# Shell check (CI script standards)

<p class="example-badges">
  <a class="example-badge example-badge--shell-check" href="../usage/reference/shell-check.md">shell-check</a>
</p>

Validate `before_script`, `script`, and `after_script` blocks with packaged
Gherkin policies. This is **not** the ShellCheck binary — standards are
executable BDD scenarios with `GLCI-SHELL-*` control IDs.

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

Findings include job name and rule IDs such as `GLCI-SHELL-PIN-002` (remote
pipe to shell) and `GLCI-SHELL-QUOTE-001` (unquoted variables).

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
#   id: GLCI-SHELL-AWS-001
#   severity: HIGH
Feature: AWS CLI tagging

  Scenario: aws create commands pass --tags
    Given I have any job with effective script defined
    Then its effective script must not match
      "aws\\s+ec2\\s+run-instances(?![^\\n]*--tags)"
```

Run with your policy directory:

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

Back to [Examples](index.md).
