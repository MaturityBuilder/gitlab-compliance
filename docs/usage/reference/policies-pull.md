<!-- gitlab-compliance-command-reference-opening-auto-generated -->
# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `target` | Yes | `text` | `None` | `target` | OCI reference to pull, for example `oci://registry.example.com/org/policies:1.0.0`. |
| `output_dir` | No | `text` | `policy` | `--output-dir, -o` | Directory to extract pulled policies into. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
<!-- gitlab-compliance-command-reference-closing-auto-generated -->
