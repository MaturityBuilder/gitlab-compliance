# get-attributes

Export selected GitLab CI job attributes as Markdown or JSON.

## Usage

```text
Usage: gitlab-compliance get-attributes [OPTIONS]
```

## Options

- `attributes`
  - Type: text
  - Default: `readme.md`
  - Usage: `--attributes, -a`

  Comma-separated list of GitLab CI YAML attributes to export.

- `OUTPUT_FILE`
  - Type: text
  - Default: `readme.md`
  - Usage: `--output-file, -o`

  Output location of the markdown documentation.

- `GLDOCS_CONFIG_FILE`
  - Type: text
  - Default: `.gitlab-ci.yml`
  - Usage: `--input-config, -i`

  GitLab CI input configuration file to read.

- `json_format`
  - Type: boolean
  - Default: `false`
  - Usage: `--json, -j`

  Return results in json format.

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`

  Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance get-attributes [OPTIONS]

  Export selected GitLab CI job attributes as Markdown or JSON.

Options:
  -a, --attributes TEXT    Comma-separated list of GitLab CI YAML attributes
                           to export.
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  GitLab CI input configuration file to read.
  -j, --json BOOLEAN       Return results in json format.
  --help                   Show this message and exit.
```
