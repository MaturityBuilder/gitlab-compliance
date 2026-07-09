# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text

Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

* `target` (REQUIRED) [argument]:
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `target`

* `output_dir`:
  * Type: STRING
  * Default: `policy`
  * Usage: `--output-dir, -o`

  Directory to extract pulled policies into.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## Examples

```bash
gitlab-compliance policies pull registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/security/
```

## CLI Help

```text

Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.

```
