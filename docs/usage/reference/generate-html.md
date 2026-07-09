# generate-html

Deprecated: use `generate --format html` instead.

> Hidden maintenance command. Deprecated command.


## Usage

```
Usage: gitlab-compliance generate-html [OPTIONS]
```

## Options

### `--detailed`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--detailed`

Will include workflow and rules from jobs.

### `-o, --output-file`

- **Type:** `STRING`
- **Default:** `gitlab-compliance.html`
- **Usage:** `-o, --output-file`

Output location of the HTML documentation.

### `-i, --input-config`

- **Type:** `STRING`
- **Default:** `.gitlab-ci.yml`
- **Usage:** `-i, --input-config`

The GitLab CI input configuration file to generate documentation from.

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance generate-html [OPTIONS]

  Deprecated: use `generate --format html` instead. (DEPRECATED)

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The GitLab CI input configuration file to generate
                           documentation from.
  --help                   Show this message and exit.
```
