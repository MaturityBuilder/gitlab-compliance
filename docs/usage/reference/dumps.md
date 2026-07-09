# dumps

Create one markdown file per subcommand under --docsPath.

> Hidden maintenance command.


## Usage

```
Usage: gitlab-compliance dumps [OPTIONS]
```

## Options

### `--baseModule` (required)

- **Type:** `STRING`
- **Default:** `src.gitlab_compliance`
- **Usage:** `--baseModule`

The base command module path to import

### `--baseCommand` (required)

- **Type:** `STRING`
- **Default:** `gitlab_compliance`
- **Usage:** `--baseCommand`

The base command function to import

### `--docsPath` (required)

- **Type:** `STRING`
- **Default:** `docs/usage/reference/`
- **Usage:** `--docsPath`

The docs dir path to write the md files

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance dumps [OPTIONS]

  Create one markdown file per subcommand under --docsPath.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```
