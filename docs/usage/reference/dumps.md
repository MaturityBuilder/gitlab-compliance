# dumps

Create one markdown file per subcommand under --docsPath.

## Usage

```text
Usage: gitlab-compliance dumps [OPTIONS]
```

## Options

### `--baseModule`

- **Name:** `base_module`
- **Kind:** Option
- **Required:** yes
- **Default:** `src.gitlab_compliance`
- **Type:** `STRING`
- **Description:** The base command module path to import

### `--baseCommand`

- **Name:** `base_command`
- **Kind:** Option
- **Required:** yes
- **Default:** `gitlab_compliance`
- **Type:** `STRING`
- **Description:** The base command function to import

### `--docsPath`

- **Name:** `docs_path`
- **Kind:** Option
- **Required:** yes
- **Default:** `docs/usage/reference/`
- **Type:** `STRING`
- **Description:** The docs dir path to write the md files


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
