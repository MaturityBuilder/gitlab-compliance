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



## .gitlab-ci.yml

## Jobs

### MEGALINTER


|      **Key**      |               **Value**                |
| :---------------: | :------------------------------------: |
| **allow_failure** |                  True                  |
|   **artifacts**   |            'when': 'always'            |
|                   |     'paths': ['megalinter-reports']    |
|                   |          'expire_in': '1 week'         |
|     **image**     |  oxsecurity/megalinter-python:v8.0.0   |
|     **stage**     |              code-quality              |
|   **variables**   | 'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR' |
### .BUILD:PYTHON


|     **Key**     |           **Value**            |
| :-------------: | :----------------------------: |
|  **artifacts**  |        'when': 'always'        |
|                 |  'paths': ['./dist/*.tar.gz']  |
|                 |      'expire_in': '1 hour'     |
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
|    **stage**     |     publish     |




[comment]: <> (gitlab-docs-closing-auto-generated)


## .gitlab-ci.yml

## Jobs

### MEGALINTER


|      **Key**      |               **Value**                |
| :---------------: | :------------------------------------: |
| **allow_failure** |                  True                  |
|   **artifacts**   |            'when': 'always'            |
|                   |     'paths': ['megalinter-reports']    |
|                   |          'expire_in': '1 week'         |
|     **image**     |  oxsecurity/megalinter-python:v8.0.0   |
|     **stage**     |              code-quality              |
|   **variables**   | 'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR' |
### .BUILD:PYTHON


|     **Key**     |           **Value**            |
| :-------------: | :----------------------------: |
|  **artifacts**  |        'when': 'always'        |
|                 |  'paths': ['./dist/*.tar.gz']  |
|                 |      'expire_in': '1 hour'     |
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
|    **stage**     |     publish     |


[comment]: <> (gitlab-docs-closing-auto-generated)
