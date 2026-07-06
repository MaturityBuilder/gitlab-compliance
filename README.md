# Gitlab Docs

## Contributing

Branch names, commit messages, and PR titles follow [Conventional Commits](https://www.conventionalcommits.org/). Every pull request must link a **user story** GitHub issue (`Closes #123`). See [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), and the [user story issue template](.github/ISSUE_TEMPLATE/user_story.yml).

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

### GitHub Actions

CI, PyPI trusted publishing, and container builds run via GitHub Actions. See [.github/workflows/README.md](.github/workflows/README.md) for PyPI publisher setup and workflow triggers.

## Using gitlab-docs

This writes documentation from `.gitlab-ci.yml` (and nested `local` includes) to `GITLAB-DOCS.md` by default. Re-runs replace only the block between the `gitlab-docs-opening-auto-generated` and `gitlab-docs-closing-auto-generated` HTML comments, so you can keep hand-written content above or below the generated section.

```bash
gitlab-docs
gitlab-docs --detailed
gitlab-docs -c .gitlab-ci.yml -o docs/ci.md
gitlab-docs --format html -o docs/ci.html
gitlab-docs --format json -o docs/ci.json
```

| Flag | Description |
| ---- | ----------- |
| `--detailed` | Include workflow rules and per-job `rules` |
| `-c`, `--config` | CI config file (overrides `GLDOCS_CONFIG_FILE`) |
| `-o`, `--output` | Output path (overrides `OUTPUT_FILE`) |
| `--format` | `markdown` (default), `html`, `json`, or `csv` |

# ENVIRONMENT VARIABLES

| Key                           | Default Value    | Description                                                                                          |
| ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| GLDOCS_CONFIG_FILE            | .gitlab-ci.yml   | The gitlab configuration file you want to generate documentation on                                  |
| OUTPUT_FILE                   | ./GITLAB-DOCS.md | The file to output documentation to                                                                  |
| OUTPUT_FORMAT                 | markdown         | Output format: markdown, html, json, or csv (non-markdown writes the full file, without merge markers) |
| LOG_LEVEL                     | INFO             | Determines the verbosity of the logging when you run gitlab-docs                                     |
| ENABLE_WORKFLOW_DOCUMENTATION | false            | When true, documents `workflow` (same as `--detailed` for workflows; job `rules` still need `--detailed`) |

## Example of what's generated
## .gitlab-ci.yml

## Jobs

### MEGALINTER

|    **Key**    |               **Value**                |
| :-----------: | :------------------------------------: |
| **artifacts** |            'when': 'always'            |
|               |    'paths': ['megalinter-reports']     |
|               |         'expire_in': '1 week'          |
|   **image**   |  oxsecurity/megalinter-python:v8.0.0   |
|   **stage**   |              code-quality              |
| **variables** | 'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR' |

### .BUILD:PYTHON

|     **Key**     |           **Value**            |
| :-------------: | :----------------------------: |
|  **artifacts**  |        'when': 'always'        |
|                 |  'paths': ['./dist/*.tar.gz']  |
|                 |     'expire_in': '1 hour'      |
| **environment** |            release             |
|  **id_tokens**  | 'PYPI_ID_TOKEN': 'aud': 'pypi' |
|    **needs**    |               []               |
|    **stage**    |              .pre              |

### BUILD

|   **Key**   |     **Value**     |
| :---------: | :---------------: |
| **extends** | ['.build:python'] |

### BUILD:DOCKER

|     **Key**      |       **Value**       |
| :--------------: | :-------------------: |
| **dependencies** |       ['build']       |
|    **image**     |     docker:latest     |
|   **services**   |    ['docker:dind']    |
|    **stage**     |         build         |
|     **tags**     | ['gitlab-org-docker'] |

### DOCKER-BUILD-MASTER

|     **Key**      |    **Value**    |
| :--------------: | :-------------: |
| **dependencies** |    ['build']    |
|    **image**     |  docker:latest  |
|   **services**   | ['docker:dind'] |
|    **stage**     |     promote     |

[comment]: <> (gitlab-docs-closing-auto-generated)
