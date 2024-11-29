

## Variables
|     Key     |   Value   | Description | Options  | Expand |
|:-----------:|:---------:|:-----------:|:--------:|:------:|
| OUTPUT_FILE | README.md |   &#x274c;  | &#x274c; |  true  |

## Jobs




## Includes

| Include Type |          Project          | Version | Valid Version | File | Variables | Rules |
|:------------:|:-------------------------:|:-------:|:-------------:|:----:|:---------:|:-----:|
|    local     | gitlab-ci/hidden.jobs.yml |   n/a   |    &#9989;    |      |           |       |



## .gitlab-ci.yml

## Jobs


### MEGALINTER


|    **Key**    |               **Value**                |
|:-------------:|:--------------------------------------:|
| **artifacts** |            'when': 'always'            |
|               |     'paths': ['megalinter-reports']    |
|               |          'expire_in': '1 week'         |
|   **image**   |  oxsecurity/megalinter-python:v8.0.0   |
|   **stage**   |           code-quality11234            |
| **variables** | 'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR' |

### BUILD:PYTHON


|     **Key**     |           **Value**            |
|:---------------:|:------------------------------:|
| **environment** |            release             |
|  **id_tokens**  | 'PYPI_ID_TOKEN': 'aud': 'pypi' |
|    **needs**    |               []               |
|    **stage**    |              .pre              |

### DOCKER-BUILD-MASTER


|   **Key**    |                                              **Value**                                               |
|:------------:|:----------------------------------------------------------------------------------------------------:|
|  **image**   |                                            docker:latest                                             |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG || $CI_COMMIT_REF_NAME == "f-code-for-includes-docs"'] |
| **services** |                                           ['docker:dind']                                            |
|  **stage**   |                                                build                                                 |

### BUILD:DOCKER


|   **Key**    |                                              **Value**                                               |
|:------------:|:----------------------------------------------------------------------------------------------------:|
|  **image**   |                                            docker:latest                                             |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG || $CI_COMMIT_REF_NAME == "f-code-for-includes-docs"'] |
| **services** |                                           ['docker:dind']                                            |
|  **stage**   |                                                build                                                 |
|   **tags**   |                                        ['gitlab-org-docker']                                         |




[comment]: <> (gitlab-docs-closing-auto-generated)