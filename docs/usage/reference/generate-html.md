# generate-html

Deprecated: use `generate --format html` instead.

## Usage

```text
Usage: gitlab-compliance generate-html [OPTIONS]
```

## Options

- `detailed`
  - Type: boolean
  - Default: `false`
  - Usage: `--detailed`

  Will include workflow and rules from jobs.

- `OUTPUT_FILE`
  - Type: text
  - Default: `gitlab-compliance.html`
  - Usage: `--output-file, -o`

  Output location of the HTML documentation.

- `GLDOCS_CONFIG_FILE`
  - Type: text
  - Default: `.gitlab-ci.yml`
  - Usage: `--input-config, -i`

  GitLab CI input configuration file to document.

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`

  Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance generate-html [OPTIONS]

  Deprecated: use `generate --format html` instead. (DEPRECATED)

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  GitLab CI input configuration file to document.
  --help                   Show this message and exit.
```
