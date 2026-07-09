<!-- gitlab-compliance-command-reference-opening-auto-generated -->
# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `features_dir` | Yes | `text` | `None` | `--features, -f` | Directory containing compliance policy `.feature` files to publish. |
| `target` | Yes | `text` | `None` | `target` | OCI registry target, for example `registry.example.com/org/policies:1.0.0`. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```
<!-- gitlab-compliance-command-reference-closing-auto-generated -->
