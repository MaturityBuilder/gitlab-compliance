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
| OUTPUT_FILE                   | ./README.md | The file to output documentation to. |
| LOG_LEVEL                     | INFO             | Determines the verbosity of the logging when you run gitlab-docs. For detailed logging set to TRACE.                                    |
| | False            | Outputting documentation for the workflow config is experimental                                     |

## Example of what's generated
<br><hr>

[comment]: <> (gitlab-docs-opening-auto-generated)

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
            <h1><span class="badge text-bg-primary">GITLAB DOCS - .gitlab-ci.yml</span></h1>


## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |



## .gitlab-ci.yml
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|     **image**     | oxsecurity/megalinter-python:8 |
|     **stage**     |              test              |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |     **Value**      |
| :----------: | :----------------: |
|   **only**   | ['merge_requests'] |
|  **stage**   |        test        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |           **Value**            |
| :-------------: | :----------------------------: |
| **environment** |            release             |
|  **id_tokens**  | 'PYPI_ID_TOKEN': 'aud': 'pypi' |
|    **stage**    |             build              |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">BUILD</span></h4>

<hr>

| **Property** | **Value** |
| :----------: | :-------: |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                    extends                     |                                                |                  .build:python                   |

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

|   **Property**   |                    **Value**                    |
| :--------------: | :---------------------------------------------: |
| **dependencies** |                    ['build']                    |
|    **image**     |                  docker:latest                  |
|    **rules**     | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
|   **services**   |                 ['docker:dind']                 |
|    **stage**     |                     publish                     |
|     **tags**     |              ['gitlab-org-docker']              |

[comment]: <> (gitlab-docs-closing-auto-generated)
