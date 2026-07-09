# get-attributes

Generate a Markdown table for selected GitLab CI YAML attributes.

## Usage

```text
Usage: gitlab-compliance get-attributes [OPTIONS]
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `attributes` | No | `text` | `README.md` | `--attributes, -a` | Pass a comma-separated list of GitLab CI YAML attributes. |
| `OUTPUT_FILE` | No | `text` | `README.md` | `--output-file, -o` | Output location of the Markdown documentation. |
| `GLDOCS_CONFIG_FILE` | No | `text` | `.gitlab-ci.yml` | `--input-config, -i` | GitLab CI input configuration file to generate documentation from. |
| `json_format` | No | `boolean` | `False` | `--json, -j` | Return results in JSON format. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance get-attributes [OPTIONS]

  Generate a Markdown table for selected GitLab CI YAML attributes.

Options:
  -a, --attributes TEXT    Pass a comma-separated list of GitLab CI YAML
                           attributes.
  -o, --output-file TEXT   Output location of the Markdown documentation.
  -i, --input-config TEXT  GitLab CI input configuration file to generate
                           documentation from.
  -j, --json BOOLEAN       Return results in JSON format.
  --help                   Show this message and exit.
```
