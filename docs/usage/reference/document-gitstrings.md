# document gitstrings

Render gitstrings documentation from CI YAML decorators or markdown fences.

## Usage

```text
Usage: gitlab-compliance document gitstrings [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `input_file` | text | no | `README.md` | `-i, --input-file` | Markdown or CI YAML (.yml) file with gitstrings decorators or fenced snippets. |
| `output_file` | text | no | `none` | `-o, --output-file, --output` | Markdown file for gitstrings marker updates. When set, all fragments write here and # @output in YAML is ignored. |
| `dry_mode` | boolean | no | `false` | `--dry-mode, -d` | Log updates without writing files. |
| `keep_source` | boolean | no | `true` | `--keep-source, --no-keep-source` | Include collapsible source YAML in the generated marker block. |
| `include_nested` | boolean | no | `false` | `--include-nested` | Walk nested local: includes on disk when documenting @render includes (-i must be .yml). Does not fetch project, component, remote, or template trees. |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance document gitstrings [OPTIONS]

  Render gitstrings documentation from CI YAML decorators or markdown fences.

Options:
  -i, --input-file TEXT           Markdown or CI YAML (.yml) file with
                                  gitstrings decorators or fenced snippets.
                                  [default: README.md]
  -o, --output-file, --output TEXT
                                  Markdown file for gitstrings marker updates.
                                  When set, all fragments write here and #
                                  @output in YAML is ignored.
  -d, --dry-mode                  Log updates without writing files.
  --keep-source / --no-keep-source
                                  Include collapsible source YAML in the
                                  generated marker block.  [default: keep-
                                  source]
  --include-nested                Walk nested local: includes on disk when
                                  documenting @render includes (-i must be
                                  .yml). Does not fetch project, component,
                                  remote, or template trees.
  --help                          Show this message and exit.
```
