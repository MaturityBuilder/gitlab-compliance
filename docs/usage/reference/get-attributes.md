# get-attributes

Export selected GitLab CI job attributes as a Markdown table or JSON.

Use this when you need a focused report for a comma-separated list of job
attributes instead of full pipeline documentation from `generate`.

## Usage

```
Usage: gitlab-compliance get-attributes [OPTIONS]
```

## Options

### `-a, --attributes`

- **Type:** `STRING`
- **Default:** `README.md`
- **Usage:** `-a, --attributes`

Pass a comma-separated list of GitLab CI YAML job attributes.

### `-o, --output-file`

- **Type:** `STRING`
- **Default:** `README.md`
- **Usage:** `-o, --output-file`

Output location of the Markdown documentation.

### `-i, --input-config`

- **Type:** `STRING`
- **Default:** `.gitlab-ci.yml`
- **Usage:** `-i, --input-config`

The GitLab CI input configuration file to generate documentation from.

### `-j, --json`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `-j, --json`

Return results in JSON format.

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance get-attributes [OPTIONS]

  Export selected GitLab CI job attributes as a Markdown table or JSON.

  Use this when you need a focused report for a comma-separated list of job
  attributes instead of full pipeline documentation from `generate`.

Options:
  -a, --attributes TEXT    Pass a comma-separated list of GitLab CI YAML job
                           attributes.
  -o, --output-file TEXT   Output location of the Markdown documentation.
  -i, --input-config TEXT  The GitLab CI input configuration file to generate
                           documentation from.
  -j, --json BOOLEAN       Return results in JSON format.
  --help                   Show this message and exit.
```
