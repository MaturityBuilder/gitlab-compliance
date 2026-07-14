# dumps

Create one markdown file per subcommand under --docsPath.

## Usage

```text
Usage: gitlab-compliance dumps [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `base_module` | text | yes | `src.gitlab_compliance` | `--baseModule` | The base command module path to import |
| `base_command` | text | yes | `gitlab_compliance` | `--baseCommand` | The base command function to import |
| `docs_path` | text | yes | `docs/usage/reference/` | `--docsPath` | The docs dir path to write the md files |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

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
