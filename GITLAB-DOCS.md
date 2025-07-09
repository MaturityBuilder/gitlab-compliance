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
