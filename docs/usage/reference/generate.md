# generate

Generate documentation from GitLab CI YAML.

## Usage

```
Usage: gitlab-compliance generate [OPTIONS]
```

## Options

### `--detailed`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--detailed`

Will include workflow and rules from jobs.

### `-f, --format`

- **Type:** `choice: markdown, swagger-markdown, html`
- **Default:** `markdown`
- **Usage:** `-f, --format`

Output format for generated documentation.

### `-d, --dry-mode`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `-d, --dry-mode`

If set will disable documentation from being written

### `-o, --output-file`

- **Type:** `STRING`
- **Usage:** `-o, --output-file`

Output location of the generated documentation.

### `-i, --input-config`

- **Type:** `STRING`
- **Default:** `.gitlab-ci.yml`
- **Usage:** `-i, --input-config`

The GitLab CI input configuration file to generate documentation from.

### `-x, --exclude`

- **Type:** `STRING`
- **Usage:** `-x, --exclude`

Comma-separated sections or job attributes to omit from output. Sections: inputs, variables, includes, workflow, jobs, container_images.

### `-g, --group-by`

- **Type:** `STRING`
- **Usage:** `-g, --group-by`

Group jobs in the Jobs section by this job attribute (e.g. stage).

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance generate [OPTIONS]

  Generate documentation from GitLab CI YAML.

Options:
  --detailed                      Will include workflow and rules from jobs.
  -f, --format [markdown|swagger-markdown|html]
                                  Output format for generated documentation.
  -d, --dry-mode                  If set will disable documentation from being
                                  written
  -o, --output-file TEXT          Output location of the generated
                                  documentation.
  -i, --input-config TEXT         The GitLab CI input configuration file to
                                  generate documentation from.
  -x, --exclude TEXT              Comma-separated sections or job attributes
                                  to omit from output. Sections: inputs,
                                  variables, includes, workflow, jobs,
                                  container_images.
  -g, --group-by TEXT             Group jobs in the Jobs section by this job
                                  attribute (e.g. stage).
  --help                          Show this message and exit.
```
