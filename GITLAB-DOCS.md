

## Variables
|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |

## Jobs




## Includes

| Include Type |          Project          | Version | Valid Version | File | Variables | Rules |
| :----------: | :-----------------------: | :-----: | :-----------: | :--: | :-------: | :---: |
|    local     | gitlab-ci/hidden.jobs.yml |   n/a   |    &#9989;    |      |           |       |



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
