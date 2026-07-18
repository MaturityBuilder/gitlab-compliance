# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```text
Usage: gitlab-compliance policies doc [OPTIONS]
```

## Options

### `--features, -f`

- **Name:** `features_dir`
- **Kind:** Option
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** Directory containing compliance policy .feature files.

### `--format`

- **Name:** `output_format`
- **Kind:** Option
- **Required:** no
- **Default:** `markdown`
- **Type:** `Choice(['markdown', 'html'])`
- **Description:** Output format for the policy catalog.

### `--output-file, -o`

- **Name:** `output_file`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Write the policy catalog to this file.


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
