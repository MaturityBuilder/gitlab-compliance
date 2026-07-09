# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

- `target` (required) [argument]
  - Type: text
  - Default: `none`
  - Usage: `target`
  - No description provided.

- `output_dir`
  - Type: text
  - Default: `policy`
  - Usage: `--output-dir, -o`
  - Directory to extract pulled policies into.

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`
  - Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
