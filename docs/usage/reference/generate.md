# generate

Will scan through your gitlab-ci yml and build documentation from the yml.

## Usage

```text
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

### `--detailed`

- **Name:** `detailed`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Will include workflow and rules from jobs.

### `--format, -f`

- **Name:** `output_format`
- **Kind:** Option
- **Required:** no
- **Default:** `markdown`
- **Type:** `Choice(['markdown', 'swagger-markdown', 'html'])`
- **Description:** Output format for generated documentation.

### `--dry-mode, -d`

- **Name:** `DRY_MODE`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** If set will disable documentation from being written

### `--output-file, -o`

- **Name:** `OUTPUT_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Output location of the generated documentation.

### `--input-config, -i`

- **Name:** `GLDOCS_CONFIG_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `.gitlab-ci.yml`
- **Type:** `STRING`
- **Description:** The Gitlab CI Input configuration file to generated documentation from.

### `--exclude, -x`

- **Name:** `exclude`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Comma-separated sections or job attributes to omit from output. Sections: inputs, variables, includes, workflow, jobs, container_images.

### `--group-by, -g`

- **Name:** `group_by`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Group jobs in the Jobs section by this job attribute (e.g. stage).


## CLI Help

```text
Usage: gitlab-compliance generate [OPTIONS]

  Will scan through your gitlab-ci yml and build documentation from the yml.

Options:
  --detailed                      Will include workflow and rules from jobs.
  -f, --format [markdown|swagger-markdown|html]
                                  Output format for generated documentation.
  -d, --dry-mode                  If set will disable documentation from being
                                  written
  -o, --output-file TEXT          Output location of the generated
                                  documentation.
  -i, --input-config TEXT         The Gitlab CI Input configuration file to
                                  generated documentation from.
  -x, --exclude TEXT              Comma-separated sections or job attributes
                                  to omit from output. Sections: inputs,
                                  variables, includes, workflow, jobs,
                                  container_images.
  -g, --group-by TEXT             Group jobs in the Jobs section by this job
                                  attribute (e.g. stage).
  --help                          Show this message and exit.
```
