# generate

Will scan through your gitlab-ci yml and build documentation from the yml.

## Usage

```text
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `detailed` | boolean | no | `false` | `--detailed` | Will include workflow and rules from jobs. |
| `output_format` | choice: `markdown`, `swagger-markdown`, `html` | no | `markdown` | `--format, -f` | Output format for generated documentation. |
| `DRY_MODE` | boolean | no | `false` | `--dry-mode, -d` | If set will disable documentation from being written |
| `OUTPUT_FILE` | text | no | `none` | `--output-file, -o` | Output location of the generated documentation. |
| `GLDOCS_CONFIG_FILE` | text | no | `.gitlab-ci.yml` | `--input-config, -i` | The Gitlab CI Input configuration file to generated documentation from. |
| `exclude` | text | no | `none` | `--exclude, -x` | Comma-separated sections or job attributes to omit from output. Sections: inputs, variables, includes, workflow, jobs, container_images. |
| `group_by` | text | no | `none` | `--group-by, -g` | Group jobs in the Jobs section by this job attribute (e.g. stage). |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

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
