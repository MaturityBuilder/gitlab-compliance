# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```text
Usage: gitlab-compliance policies doc [OPTIONS]
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `features_dir` | Yes | `text` | `None` | `--features, -f` | Directory containing compliance policy `.feature` files. |
| `output_format` | No | `choice: markdown, html` | `markdown` | `--format` | Output format for the policy catalog. |
| `output_file` | No | `text` | `None` | `--output-file, -o` | Write the policy catalog to this file. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance policies doc [OPTIONS]

  Generate a searchable policy catalog from Conftest-style # METADATA
  annotations.

Options:
  -f, --features TEXT       Directory containing compliance policy .feature
                            files.  [required]
  --format [markdown|html]  Output format for the policy catalog.
  -o, --output-file TEXT    Write the policy catalog to this file.
  --help                    Show this message and exit.
```
