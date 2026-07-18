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

### `--attributes, -a`

- **Name:** `attributes`
- **Kind:** Option
- **Required:** no
- **Default:** `README.md`
- **Type:** `STRING`
- **Description:** Pass a comma seperated list of gitlab ci yml attributes

### `--output-file, -o`

- **Name:** `OUTPUT_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `README.md`
- **Type:** `STRING`
- **Description:** Output location of the markdown documentation.

### `--input-config, -i`

- **Name:** `GLDOCS_CONFIG_FILE`
- **Kind:** Option
- **Required:** no
- **Default:** `.gitlab-ci.yml`
- **Type:** `STRING`
- **Description:** The Gitlab CI Input configuration file to generated documentation from.

### `--json, -j`

- **Name:** `json_format`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Return results in json format.


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
  --help                   Show this message and exit.
```
