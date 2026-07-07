# generate

Will scan through your gitlab-ci yml and build documentation from the yml.

### Usage

```
Usage: gitlab-compliance generate [OPTIONS]
```

### Options
* `detailed`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.

* `output_format`:
  * Type: Choice(['markdown', 'html'])
  * Default: `markdown`
  * Usage: `--format
-f`

  Output format for generated documentation.

* `DRY_MODE`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written

* `OUTPUT_FILE`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file
-o`

  Output location of the generated documentation.

* `GLDOCS_CONFIG_FILE`:
  * Type: STRING
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


### CLI Help

```
Usage: gitlab-compliance generate [OPTIONS]

  Will scan through your gitlab-ci yml and build documentation from the yml.

Options:
  --detailed                    Will include workflow and rules from jobs.
  -f, --format [markdown|html]  Output format for generated documentation.
  -d, --dry-mode                If set will disable documentation from being
                                written
  -o, --output-file TEXT        Output location of the generated
                                documentation.
  -i, --input-config TEXT       The Gitlab CI Input configuration file to
                                generated documentation from.
  --help                        Show this message and exit.
```
