# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `target argument` | STRING | `required` | Show this message and exit. |
| `--output-dir, -o` | STRING | `policy` | Directory to extract pulled policies into. |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
