# document gitstrings

Render gitstrings documentation from CI YAML decorators or markdown fences.

<!-- MANUAL DOCS:START -->

## See it in action

![gitlab-compliance document gitstrings](../../demos/gifs/document-gitstrings.gif)

<!-- MANUAL DOCS:END -->






## Usage

```
Usage: gitlab-compliance document gitstrings [OPTIONS]
```

## Options
* `input_file`:
  * Type: STRING
  * Default: `readme.md`
  * Usage: `-i
--input-file`

  Markdown or CI YAML (.yml) file with gitstrings decorators or fenced snippets.

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `-o
--output-file
--output`

  Markdown file for gitstrings marker updates. When set, all fragments write here and # @output in YAML is ignored.

* `dry_mode`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--dry-mode
-d`

  Log updates without writing files.

* `keep_source`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--keep-source`

  Include collapsible source YAML in the generated marker block.

* `include_nested`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--include-nested`

  Walk nested local: includes on disk when documenting @render includes (-i must be .yml). Does not fetch project, component, remote, or template trees.

* `max_include_depth`:
  * Type: INT
  * Default: `none`
  * Usage: `--max-include-depth`

  Max local include nesting depth from the root file (omit for unlimited).

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
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
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  --help                          Show this message and exit.
```
