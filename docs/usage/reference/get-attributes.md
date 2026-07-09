# get-attributes

Build a Markdown table or JSON payload for selected GitLab CI job attributes.

## Usage

```text
Usage: gitlab-compliance get-attributes [OPTIONS]
```

## Options

- `attributes`
  - Type: text
  - Default: `README.md`
  - Usage: `--attributes, -a`
  - Comma-separated list of GitLab CI YAML job attributes to document.

- `OUTPUT_FILE`
  - Type: text
  - Default: `README.md`
  - Usage: `--output-file, -o`
  - Output location of the markdown documentation.

- `GLDOCS_CONFIG_FILE`
  - Type: text
  - Default: `.gitlab-ci.yml`
  - Usage: `--input-config, -i`
  - GitLab CI YAML file to read.

- `json_format`
  - Type: boolean
  - Default: `false`
  - Usage: `--json, -j`
  - Return results in JSON format.

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`
  - Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance get-attributes [OPTIONS]

  Build a Markdown table or JSON payload for selected GitLab CI job
  attributes.

Options:
  -a, --attributes TEXT    Comma-separated list of GitLab CI YAML job
                           attributes to document.
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  GitLab CI YAML file to read.
  -j, --json BOOLEAN       Return results in JSON format.
  --help                   Show this message and exit.
```
