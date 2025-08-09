# Gitlab Docs

## How to install

Gitlab Docs is portable utility based in python so any system that supports python3 you will be able to install it.

### Python

```bash
pip3 install --user gitlab-docs
```

### Docker

```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```
or

```bash
podman run -it -v $(PWD):/gitlab-docs charlieasmith93/gitlab-docs
```
## Using gitlab-docs

This will output the results in the current working directory to `GITLAB-DOCS.md` based on the `.gitlab-ci.yml` config. Noting it will also automatically try to detect and produce documentation for any include configurations as well.

```
gitlab-docs

```

# ENVIRONMENT VARIABLES

| Key                           | Default Value    | Description                                                                                          |
| ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| GLDOCS_CONFIG_FILE            | .gitlab-ci.yml   | The gitlab configuration file you want to generate documentation on                                  |
| OUTPUT_FILE                   | ./README.md | The file to output documentation to. |
| LOG_LEVEL                     | INFO             | Determines the verbosity of the logging when you run gitlab-docs. For detailed logging set to TRACE.                                    |
| | False            | Outputting documentation for the workflow config is experimental                                     |

## Example of what's generated
<br><hr>

[comment]: <> (gitlab-docs-opening-auto-generated)

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
            <h1><span class="badge text-bg-primary">GITLAB DOCS - .gitlab-ci.yml</span></h1>
[comment]: <> (gitlab-docs-closing-auto-generated)
