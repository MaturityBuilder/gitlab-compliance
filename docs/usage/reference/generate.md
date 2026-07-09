# generate

Generate pipeline documentation from a GitLab CI YAML file.

## Usage

```text
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

- `detailed`
  - Type: boolean
  - Default: `false`
  - Usage: `--detailed`
  - Will include workflow and rules from jobs.

- `output_format`
  - Type: choice: `markdown`, `swagger-markdown`, `html`
  - Default: `markdown`
  - Usage: `--format, -f`
  - Output format for generated documentation.

- `DRY_MODE`
  - Type: boolean
  - Default: `false`
  - Usage: `--dry-mode, -d`
  - If set will disable documentation from being written

- `OUTPUT_FILE`
  - Type: text
  - Default: `none`
  - Usage: `--output-file, -o`
  - Output location of the generated documentation.

- `GLDOCS_CONFIG_FILE`
  - Type: text
  - Default: `.gitlab-ci.yml`
  - Usage: `--input-config, -i`
  - GitLab CI YAML file to read.

- `exclude`
  - Type: text
  - Default: `none`
  - Usage: `--exclude, -x`
  - Comma-separated sections or job attributes to omit from output. Sections: inputs, variables, includes, workflow, jobs, container_images.

- `group_by`
  - Type: text
  - Default: `none`
  - Usage: `--group-by, -g`
  - Group jobs in the Jobs section by this job attribute (e.g. stage).

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`
  - Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance generate [OPTIONS]

  Generate pipeline documentation from a GitLab CI YAML file.

Options:
  --detailed                      Will include workflow and rules from jobs.
  -f, --format [markdown|swagger-markdown|html]
                                  Output format for generated documentation.
  -d, --dry-mode                  If set will disable documentation from being
                                  written
  -o, --output-file TEXT          Output location of the generated
                                  documentation.
  -i, --input-config TEXT         GitLab CI YAML file to read.
  -x, --exclude TEXT              Comma-separated sections or job attributes
                                  to omit from output. Sections: inputs,
                                  variables, includes, workflow, jobs,
                                  container_images.
  -g, --group-by TEXT             Group jobs in the Jobs section by this job
                                  attribute (e.g. stage).
  --help                          Show this message and exit.
```
