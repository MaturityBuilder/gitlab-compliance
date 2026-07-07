# compliance-pull

Pull a compliance policy bundle from an OCI registry.

### Usage

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET
```

### Options
* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
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


### CLI Help

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
