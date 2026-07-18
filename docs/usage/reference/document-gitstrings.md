# document gitstrings

Render gitstrings documentation from CI YAML decorators or markdown fences.

## Usage

```text
Usage: gitlab-compliance document gitstrings [OPTIONS]
```

## Options

### `-i, --input-file`

- **Name:** `input_file`
- **Kind:** Option
- **Required:** no
- **Default:** `README.md`
- **Type:** `STRING`
- **Description:** Markdown or CI YAML (.yml) file with gitstrings decorators or fenced snippets.

### `-o, --output-file, --output`

- **Name:** `output_file`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Markdown file for gitstrings marker updates. When set, all fragments write here and # @output in YAML is ignored.

### `--dry-mode, -d`

- **Name:** `dry_mode`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Log updates without writing files.

### `--keep-source, --no-keep-source`

- **Name:** `keep_source`
- **Kind:** Option
- **Required:** no
- **Default:** `true`
- **Type:** `BOOL`
- **Description:** Include collapsible source YAML in the generated marker block.

### `--include-nested`

- **Name:** `include_nested`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Walk nested local: includes on disk when documenting @render includes (-i must be .yml). Does not fetch project, component, remote, or template trees.


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
