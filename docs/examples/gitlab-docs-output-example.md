
[comment]: <> (gitlab-compliance-opening-auto-generated)

# GITLAB COMPLIANCE - .gitlab-ci.yml

## Inputs

|    Key    |        Value        | Description | Options  | Expand |
| :-------: | :-----------------: | :---------: | :------: | :----: |
| job-stage | {'default': 'test'} |   &#x274c;  | &#x274c; |  true  |


## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| APPLICATION |  gitlab-compliance   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | gitlab-compliance.md |   &#x274c;  | &#x274c; |  true  |

## Jobs
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Attribute** | **Value** |
| :-----------: | :-------: |
|   **stage**   |    test   |

| Rule # |                      if                      |  when |
| :----: | :------------------------------------------: | :---: |
|   1    |                $CI_COMMIT_TAG                | never |
|   2    | $CI_PIPELINE_SOURCE == "merge_request_event" |       |
|   3    |   $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH    |       |

<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|   **Attribute**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |         1. .test:rules         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |


<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Attribute** |   **Value**    |
| :-----------: | :------------: |
|  **extends**  | 1. .test:rules |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |           POETRY_VIRTUALENVS_CREATE            |                      false                       |


<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Attribute** |   **Value**    |
| :-----------: | :------------: |
|   **image**   | python:3.12.11 |
|   **stage**   |    publish     |

| Rule # |              if             |
| :----: | :-------------------------: |
|   1    | $CI_COMMIT_BRANCH == "main" |

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|  **Attribute**  | **Value** |
| :-------------: | :-------: |
| **environment** |  release  |
|    **stage**    |   build   |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Attribute** |    **Value**     |
| :-----------: | :--------------: |
|  **extends**  | 1. .build:python |
|               |  2. .test:rules  |

<h4><span class="badge text-bg-info">DOCS:REVIEW</span></h4>

<hr>

| **Attribute** |    **Value**    |
| :-----------: | :-------------: |
|  **extends**  | 1. .docs:mkdocs |
|               |  2. .test:rules |
|   **stage**   |      build      |

<h4><span class="badge text-bg-info">PAGES</span></h4>

<hr>

| **Attribute** |  **Value**   |
| :-----------: | :----------: |
|  **extends**  | .docs:mkdocs |
|   **stage**   |   publish    |

| Rule # |                    if                   |
| :----: | :-------------------------------------: |
|   1    | $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH |

<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Attribute**  | **Value** |
| :-------------: | :-------: |
|    **cache**    |     []    |
| **environment** |  release  |
|    **stage**    |  publish  |

| Rule # |       if       |
| :----: | :------------: |
|   1    | $CI_COMMIT_TAG |

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Attribute** |      **Value**       |
| :-----------: | :------------------: |
|   **image**   |    docker:latest     |
|  **services** |    1. docker:dind    |
|   **stage**   |        build         |
|    **tags**   | 1. gitlab-org-docker |

| Rule # |                   if                  |
| :----: | :-----------------------------------: |
|   1    | $CI_COMMIT_REF_NAME != $CI_COMMIT_TAG |

[comment]: <> (gitlab-compliance-closing-auto-generated)
