# generate-html

Deprecated: use `generate --format html` instead.

## Usage

```text
Usage: gitlab-compliance generate-html [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--detailed` | BOOL | `false` | Include workflow and per-job rules in generated documentation. |
| `--output-file, -o` | STRING | `gitlab-compliance.html` | Output location of the HTML documentation. |
| `--input-config, -i` | STRING | `.gitlab-ci.yml` | GitLab CI YAML file to document. |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance generate-html [OPTIONS]

  Deprecated: use `generate --format html` instead. (DEPRECATED)

Options:
  --detailed               Include workflow and per-job rules in generated
                           documentation.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  GitLab CI YAML file to document.
  --help                   Show this message and exit.
```
