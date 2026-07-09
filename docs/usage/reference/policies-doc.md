# policies doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

## Usage

```text

Usage: gitlab-compliance policies doc [OPTIONS]

```

## Options

* `features_dir` (REQUIRED):
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `--features, -f`

  Directory containing compliance policy .feature files.

* `output_format`:
  * Type: Choice(['markdown', 'html'])
  * Default: `markdown`
  * Usage: `--format`

  Output format for the policy catalog.

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file, -o`

  Write the policy catalog to this file.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## Examples

```bash
gitlab-compliance policies doc -f policies/security/ -o policy-catalog.md
gitlab-compliance policies doc -f policies/security/ --format html -o policy-catalog.html
```

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
