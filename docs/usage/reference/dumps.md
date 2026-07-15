# dumps

Create one markdown file per subcommand under --docsPath.

## Usage

```text
Usage: gitlab-compliance dumps [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--baseModule` | STRING | `required` | The base command module path to import |
| `--baseCommand` | STRING | `required` | The base command function to import |
| `--docsPath` | STRING | `required` | The docs dir path to write the md files |
| `--help` | BOOL | `false` | Show this message and exit. |


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
