# dumps

Create one markdown file per subcommand under --docsPath.

## Usage

```text
Usage: gitlab-compliance dumps [OPTIONS]
```

## Options

* `base_module` (REQUIRED):
  * Type: STRING
  * Default: `src.gitlab_compliance`
  * Usage: `--baseModule`

  The base command module path to import

* `base_command` (REQUIRED):
  * Type: STRING
  * Default: `gitlab_compliance`
  * Usage: `--baseCommand`

  The base command function to import

* `docs_path` (REQUIRED):
  * Type: STRING
  * Default: `docs/usage/reference/`
  * Usage: `--docsPath`

  The docs dir path to write the md files

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## CLI Help

```text
Usage: gitlab-compliance dumps [OPTIONS]

  Create one markdown file per subcommand under --docsPath.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```
