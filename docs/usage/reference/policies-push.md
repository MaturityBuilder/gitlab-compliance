# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```text

Usage: gitlab-compliance policies push [OPTIONS] TARGET

```

## Options

* `features_dir` (REQUIRED):
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `--features, -f`

Directory containing compliance policy .feature files to publish.

* `target` (REQUIRED) [argument]:
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `target`

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## Examples

```bash
gitlab-compliance policies push -f policies/security/ registry.example.com/org/gitlab-ci-policies:1.0.0
```

## CLI Help

```text

Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.

```
