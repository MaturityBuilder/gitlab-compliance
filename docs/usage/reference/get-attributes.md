# get-attributes

Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
    Args:
        OUTPUT_FILE (_type_): _description_
        GLDOCS_CONFIG_FILE (_type_): _description_
        attributes (_type_): _description_
        json (_type_): _description_

## Usage

```text

Usage: gitlab-compliance get-attributes [OPTIONS]

```

## Options

* `attributes`:
  * Type: STRING
  * Default: `readme.md`
  * Usage: `--attributes, -a`

  Pass a comma seperated list of gitlab ci yml attributes

* `OUTPUT_FILE`:
  * Type: STRING
  * Default: `readme.md`
  * Usage: `--output-file, -o`

  Output location of the markdown documentation.

* `GLDOCS_CONFIG_FILE`:
  * Type: STRING
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config, -i`

  The Gitlab CI Input configuration file to generated documentation from.

* `json_format`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--json, -j`

  Return results in json format.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## Examples

```bash
gitlab-compliance get-attributes -i .gitlab-ci.yml -a stage,image,rules -o attributes.md
gitlab-compliance get-attributes -i .gitlab-ci.yml -a image -j true
```

## CLI Help

```text

Usage: gitlab-compliance get-attributes [OPTIONS]

  Compared to the generate command, the get-attribute command allows you to
  pass the properties you wish to document and produces a markdown table.
  Args:     OUTPUT_FILE (_type_): _description_     GLDOCS_CONFIG_FILE
  (_type_): _description_     attributes (_type_): _description_     json
  (_type_): _description_

Options:
  -a, --attributes TEXT    Pass a comma seperated list of gitlab ci yml
                           attributes
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  -j, --json BOOLEAN       Return results in json format.
  --help
              Show this message and exit.

```
