# generate

Generate pipeline documentation from GitLab CI YAML.

## Usage

```text
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `detailed` | No | `boolean` | `False` | `--detailed` | Include workflow and rules from jobs. |
| `output_format` | No | `choice: markdown, swagger-markdown, html` | `markdown` | `--format, -f` | Output format for generated documentation. |
| `DRY_MODE` | No | `boolean` | `False` | `--dry-mode, -d` | Print planned output without writing documentation. |
| `OUTPUT_FILE` | No | `text` | `None` | `--output-file, -o` | Output location of the generated documentation. |
| `GLDOCS_CONFIG_FILE` | No | `text` | `.gitlab-ci.yml` | `--input-config, -i` | GitLab CI input configuration file to generate documentation from. |
| `exclude` | No | `text` | `None` | `--exclude, -x` | Comma-separated sections or job attributes to omit from output. Sections: `inputs`, `variables`, `includes`, `workflow`, `jobs`, `container_images`. |
| `group_by` | No | `text` | `None` | `--group-by, -g` | Group jobs in the Jobs section by this job attribute, for example `stage`. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance generate [OPTIONS]

  Generate pipeline documentation from GitLab CI YAML.

Options:
  --detailed                      Will include workflow and rules from jobs.
  -f, --format [markdown|swagger-markdown|html]
                                  Output format for generated documentation.
  -d, --dry-mode                  Print planned output without writing
                                  documentation.
  -o, --output-file TEXT          Output location of the generated
                                  documentation.
  -i, --input-config TEXT         GitLab CI input configuration file to generate
                                  documentation from.
  -x, --exclude TEXT              Comma-separated sections or job attributes
                                  to omit from output. Sections: inputs,
                                  variables, includes, workflow, jobs,
                                  container_images.
  -g, --group-by TEXT             Group jobs in the Jobs section by this job
                                  attribute (e.g. stage).
  --help                          Show this message and exit.
```
