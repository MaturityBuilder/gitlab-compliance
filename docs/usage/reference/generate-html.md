# generate-html

Deprecated: use `generate --format html` instead.

## Usage

```text
Usage: gitlab-compliance generate-html [OPTIONS]
```

## Options

### `--detailed`

- **Name:** `detailed`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Will include workflow and rules from jobs.

### `--output-file, -o`

- **Name:** `OUTPUT_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `gitlab-compliance.html`
- **Type:** `STRING`
- **Description:** Output location of the HTML documentation.

### `--input-config, -i`

- **Name:** `GLDOCS_CONFIG_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `.gitlab-ci.yml`
- **Type:** `STRING`
- **Description:** The Gitlab CI Input configuration file to generated documentation from.


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
