# Command Reference
## gitlab-docs

A command line tool to convert your gitlab-ci yml into markdown documentation.

### Usage

```
Usage: gitlab-docs [OPTIONS] COMMAND [ARGS]...
```

### Options
* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-docs [OPTIONS] COMMAND [ARGS]...

  A command line tool to convert your gitlab-ci yml into markdown
  documentation.

Options:
  --help  Show this message and exit.

Commands:
  generate        Will scan through your gitlab-ci yml and build a markdown...
  get-attributes  Compared to the generate command, the get-attribute...
```


##  get-attributes

Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
Args:
    OUTPUT_FILE (_type_): _description_
    DRY_MODE (_type_): _description_
    GLDOCS_CONFIG_FILE (_type_): _description_
    attributes (_type_): _description_
    json (_type_): _description_

### Usage

```
Usage: gitlab-docs get-attributes [OPTIONS]
```

### Options
* `attributes`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--attributes
-a`

  Pass a comma seperated list of gitlab ci yml attributes


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `json`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--json
-j`

  Return results in json format.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-docs get-attributes [OPTIONS]

  Compared to the generate command, the get-attribute command allows you to
  pass the properties you wish to document and produces a markdown table.
  Args:     OUTPUT_FILE (_type_): _description_     DRY_MODE (_type_):
  _description_     GLDOCS_CONFIG_FILE (_type_): _description_
  attributes (_type_): _description_     json (_type_): _description_

Options:
  -a, --attributes TEXT    Pass a comma seperated list of gitlab ci yml
                           attributes

  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.

  -j, --json BOOLEAN       Return results in json format.
  --help                   Show this message and exit.
```


##  dumps

# Click-md
Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.

### Usage

```
Usage: gitlab-docs dumps [OPTIONS]
```

### Options
* `basemodule` (REQUIRED): 
  * Type: STRING 
  * Default: `src.gitlab_docs`
  * Usage: `--baseModule`

  The base command module path to import


* `basecommand` (REQUIRED): 
  * Type: STRING 
  * Default: `gitlab_docs`
  * Usage: `--baseCommand`

  The base command function to import


* `docspath` (REQUIRED): 
  * Type: STRING 
  * Default: `docs/`
  * Usage: `--docsPath`

  The docs dir path to write the md files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-docs dumps [OPTIONS]

  # Click-md Create md files per each command, in format of `parent-
  command`, under the `--docsPath` directory.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```


##  generate

Will scan through your gitlab-ci yml and build a markdown document from  the yml.

### Usage

```
Usage: gitlab-docs generate [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `DRY_MODE`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


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
Usage: gitlab-docs generate [OPTIONS]

  Will scan through your gitlab-ci yml and build a markdown document from
  the yml.

Options:
  --detailed               Will include workflow and rules from jobs.
  -d, --dry-mode           If set will disable documentation from being
                           written

  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.

  --help                   Show this message and exit.
```

