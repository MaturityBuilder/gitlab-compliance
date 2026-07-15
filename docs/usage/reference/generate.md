# generate

Generate pipeline documentation from GitLab CI YAML.

## Usage

```text
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--detailed` | BOOL | `false` | Include workflow and per-job rules in generated documentation. |
| `--format, -f` | markdown, swagger-markdown, html | `markdown` | Output format for generated documentation. |
| `--dry-mode, -d` | BOOL | `false` | Preview the command without writing documentation. |
| `--output-file, -o` | STRING | `none` | Output location of the generated documentation. |
| `--input-config, -i` | STRING | `.gitlab-ci.yml` | GitLab CI YAML file to document. |
| `--exclude, -x` | STRING | `none` | Comma-separated sections or job attributes to omit from output. Sections: inputs, variables, includes, workflow, jobs, container_images. |
| `--group-by, -g` | STRING | `none` | Group jobs in the Jobs section by this job attribute (e.g. stage). |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance generate [OPTIONS]

  Generate pipeline documentation from GitLab CI YAML.

Options:
  --detailed                      Include workflow and per-job rules in
                                  generated documentation.
  -f, --format [markdown|swagger-markdown|html]
                                  Output format for generated documentation.
  -d, --dry-mode                  Preview the command without writing
                                  documentation.
  -o, --output-file TEXT          Output location of the generated
                                  documentation.
  -i, --input-config TEXT         GitLab CI YAML file to document.
  -x, --exclude TEXT              Comma-separated sections or job attributes
                                  to omit from output. Sections: inputs,
                                  variables, includes, workflow, jobs,
                                  container_images.
  -g, --group-by TEXT             Group jobs in the Jobs section by this job
                                  attribute (e.g. stage).
  --help                          Show this message and exit.
```
