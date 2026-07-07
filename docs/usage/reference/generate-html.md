# generate-html

Deprecated: use `generate --format html` instead.

### Usage

```
Usage: gitlab-compliance generate-html [OPTIONS]
```

### Options
* `detailed`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.

* `OUTPUT_FILE`:
  * Type: STRING
  * Default: `gitlab-compliance.html`
  * Usage: `--output-file
-o`

  Output location of the HTML documentation.

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
Usage: gitlab-compliance generate-html [OPTIONS]

  Deprecated: use `generate --format html` instead. (DEPRECATED)

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  --help                   Show this message and exit.
```
