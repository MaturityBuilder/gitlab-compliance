# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--features, -f` | STRING | `required` | Directory containing compliance policy .feature files to publish. |
| `target argument` | STRING | `required` | Show this message and exit. |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```
