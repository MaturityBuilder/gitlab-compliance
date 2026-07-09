# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```
Usage: gitlab-compliance policies doc [OPTIONS]
```

## Options

### `-f, --features` (required)

- **Type:** `STRING`
- **Usage:** `-f, --features`

Directory containing compliance policy .feature files.

### `--format`

- **Type:** `choice: markdown, html`
- **Default:** `markdown`
- **Usage:** `--format`

Output format for the policy catalog.

### `-o, --output-file`

- **Type:** `STRING`
- **Usage:** `-o, --output-file`

Write the policy catalog to this file.

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
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
