
# Gitlab Docs

## .gitlab-ci.yml

|     Key     |   Value   | Description | Options  | Expand |
|:-----------:|:---------:|:-----------:|:--------:|:------:|
| OUTPUT_FILE | README.md |   &#x274c;  | &#x274c; |  true  |

## Jobs



### megalinter

|                                 artifacts                                  |                image                |    stage     |                variables                 |
|:--------------------------------------------------------------------------:|:-----------------------------------:|:------------:|:----------------------------------------:|
| {'when': 'always', 'paths': ['megalinter-reports'], 'expire_in': '1 week'} | oxsecurity/megalinter-python:v8.0.0 | code-quality | {'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR'} |

### docker-build-master

|     image     |                                                 rules                                                  |     services    | stage |
|:-------------:|:------------------------------------------------------------------------------------------------------:|:---------------:|:-----:|
| docker:latest | [{'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG || $CI_COMMIT_REF_NAME == "f-code-for-includes-docs"'}] | ['docker:dind'] | build |

### build:docker

|     image     |                                                 rules                                                  |     services    | stage |          tags         |
|:-------------:|:------------------------------------------------------------------------------------------------------:|:---------------:|:-----:|:---------------------:|
| docker:latest | [{'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG || $CI_COMMIT_REF_NAME == "f-code-for-includes-docs"'}] | ['docker:dind'] | build | ['gitlab-org-docker'] |



[comment]: <> (gitlab-docs-closing-auto-generated)