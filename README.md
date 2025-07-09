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

## Using gitlab-docs

This will output the results in the current working directory to `GITLAB-DOCS.md` based on the `.gitlab-ci.yml` config. Noting it will also automatically try to detect and produce documentation for any include configurations as well.

```
gitlab-docs

```

# ENVIRONMENT VARIABLES

| Key                           | Default Value    | Description                                                                                          |
| ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| GLDOCS_CONFIG_FILE            | .gitlab-ci.yml   | The gitlab configuration file you want to generate documentation on                                  |
| OUTPUT_FILE                   | ./GITLAB-DOCS.md | The file to output documentation to (WARNING outputting to README.md will overwrite file at present) |
| LOG_LEVEL                     | INFO             | Determines the verbosity of the logging when you run gitlab-docs                                     |
| ENABLE_WORKFLOW_DOCUMENTATION | False            | Outputting documentaton for the workflow config is experiemental                                     |

<!-- ### Precommit Hook -->
<!-- ```yml

``` -->
