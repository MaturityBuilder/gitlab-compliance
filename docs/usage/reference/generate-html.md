# generate-html

Deprecated: use `generate --format html` instead.

## Usage

```text
Usage: gitlab-compliance generate-html [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `detailed` | boolean | no | `false` | `--detailed` | Will include workflow and rules from jobs. |
| `OUTPUT_FILE` | text | no | `gitlab-compliance.html` | `--output-file, -o` | Output location of the HTML documentation. |
| `GLDOCS_CONFIG_FILE` | text | no | `.gitlab-ci.yml` | `--input-config, -i` | The Gitlab CI Input configuration file to generated documentation from. |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance generate-html [OPTIONS]

  Deprecated: use `generate --format html` instead. (DEPRECATED)

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  --help                   Show this message and exit.
```
