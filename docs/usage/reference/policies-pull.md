# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `target` _(argument)_ | text | yes | _not set_ | `target` |  |
| `output_dir` | text | no | `policy` | `--output-dir, -o` | Directory to extract pulled policies into. |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
