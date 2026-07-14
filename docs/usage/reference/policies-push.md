# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `features_dir` | text | yes | _not set_ | `--features, -f` | Directory containing compliance policy .feature files to publish. |
| `target` _(argument)_ | text | yes | _not set_ | `target` |  |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```
