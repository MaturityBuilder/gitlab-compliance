# Script steps

Steps for policies that inspect composed GitLab CI job scripts
(`before_script`, `script`, `after_script`, and `effective_script`).

## Given

- `Given I have any job with effective script defined`
- `Given I have any job with script defined`
- `Given I have any job with before_script defined`

## When

- `When a variable is expanded within a command`
- `When variables are used as part of a path`
- `When command substitution is used`
- `When an array is expanded`
- `When the effective script has more than 1 line`
- `When a pipeline is used`
- `When rm is used recursively`
- `When temporary files are required`

## Then

- `Then the variable must be wrapped in double quotes`
- `Then pipefail must be enabled`
- `Then eval must not be used`
- `Then untrusted remote scripts must not be executed`
- `Then script downloads must verify checksums`
- `Then package installs of type "{manager}" must use pinned versions`
- `Then unresolved script references must not be present`

Existing property matchers also work once scripts are on job entities:

```gherkin
Then its effective script must not match "curl[^\\n]*\\|\\s*(ba)?sh"
```
