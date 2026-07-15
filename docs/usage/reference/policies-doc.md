# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```text
Usage: gitlab-compliance policies doc [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--features, -f` | STRING | `required` | Directory containing compliance policy .feature files. |
| `--format` | markdown, html | `markdown` | Output format for the policy catalog. |
| `--output-file, -o` | STRING | `none` | Write the policy catalog to this file. |
| `--help` | BOOL | `false` | Show this message and exit. |


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
