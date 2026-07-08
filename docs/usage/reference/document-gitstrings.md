# gitstrings

Render decorated ```yaml gitstrings fences into marker-delimited markdown tables.

### Usage

```
Usage: gitlab-compliance document gitstrings [OPTIONS]
```

### Options

* `input_file`:
  * Type: STRING
  * Default: `README.md`
  * Usage: `--input-file
-i`

  Markdown file to scan for ```yaml gitstrings fences (source snippets).

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file
-o
--output`

  Default markdown file for gitstrings marker updates when a fence has no `# @output`.

* `dry_mode`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--dry-mode
-d`

  Log updates without writing files.

* `keep_source`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--keep-source
--no-keep-source`

  Include collapsible source YAML in the generated marker block.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

### CLI Help

```
Usage: gitlab-compliance document gitstrings [OPTIONS]

  Render decorated ```yaml gitstrings fences into marker-delimited markdown
  tables.

Options:
  -i, --input-file TEXT       Markdown file to scan for ```yaml gitstrings
                              fences (source snippets).  [default: README.md]
  -o, --output-file, --output TEXT
                              Default markdown file for gitstrings marker
                              updates when a fence has no # @output.
  -d, --dry-mode              Log updates without writing files.
  --keep-source / --no-keep-source
                              Include collapsible source YAML in the generated
                              marker block.  [default: keep-source]
  --help                      Show this message and exit.
```

See also [Gitstrings user guide](../../usage/gitstrings.md).
