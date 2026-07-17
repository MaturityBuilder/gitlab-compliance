# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```text
Usage: gitlab-compliance policies doc [OPTIONS]
```

## Options

- `features_dir` (required)
  - Type: text
  - Default: _required_
  - Usage: `--features, -f`

  Directory containing compliance policy .feature files.

- `output_format`
  - Type: choice: markdown|html
  - Default: `markdown`
  - Usage: `--format`

  Output format for the policy catalog.

- `output_file`
  - Type: text
  - Default: _not set_
  - Usage: `--output-file, -o`

  Write the policy catalog to this file.

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`

  Show this message and exit.


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
