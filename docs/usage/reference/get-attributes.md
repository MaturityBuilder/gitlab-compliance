# get-attributes

Export selected GitLab CI job attributes as a Markdown table or JSON payload.

## Usage

```text
Usage: gitlab-compliance get-attributes [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--attributes, -a` | STRING | `README.md` | Comma-separated GitLab CI YAML job attributes to document. |
| `--output-file, -o` | STRING | `README.md` | Output location for the generated Markdown table. |
| `--input-config, -i` | STRING | `.gitlab-ci.yml` | GitLab CI YAML file to inspect. |
| `--json, -j` | BOOL | `false` | Return results in JSON format. |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance get-attributes [OPTIONS]

  Export selected GitLab CI job attributes as a Markdown table or JSON
  payload.

Options:
  -a, --attributes TEXT    Comma-separated GitLab CI YAML job attributes to
                           document.
  -o, --output-file TEXT   Output location for the generated Markdown table.
  -i, --input-config TEXT  GitLab CI YAML file to inspect.
  -j, --json BOOLEAN       Return results in JSON format.
  --help                   Show this message and exit.
```
