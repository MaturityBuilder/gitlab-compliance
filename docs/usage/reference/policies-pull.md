# policies pull

Pull a compliance policy bundle from an OCI registry.

<!-- MANUAL DOCS:START -->

## See it in action

See [policies push](policies-push.md#see-it-in-action) for the combined
push/pull live demo (`docs/demos/tapes/policies-push-pull.tape`).

<!-- MANUAL DOCS:END -->






## Usage

```
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
  * Usage: `--output-dir
-o`

  Directory to extract pulled policies into.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
