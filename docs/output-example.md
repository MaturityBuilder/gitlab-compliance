
[comment]: <> (gitlab-docs-opening-auto-generated)

# GITLAB DOCS - .gitlab-ci.yml

## Inputs

+-------------+---------------------------+-------------+----------+--------+
|     Key     |           Value           | Description | Options  | Expand |
+-------------+---------------------------+-------------+----------+--------+
| environment | {'default': 'production'} |   &#x274c;  | &#x274c; |  true  |
|  job-stage  |    {'default': 'test'}    |   &#x274c;  | &#x274c; |  true  |
+-------------+---------------------------+-------------+----------+--------+


## Variables

+-------------+----------------+-------------+----------+--------+
|     Key     |     Value      | Description | Options  | Expand |
+-------------+----------------+-------------+----------+--------+
| APPLICATION |  gitlab-docs   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |
+-------------+----------------+-------------+----------+--------+

## Jobs
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

+---------------+-------------------------------------------------------+
| **Attribute** |                       **Value**                       |
+---------------+-------------------------------------------------------+
|   **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|               |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|   **stage**   |                          test                         |
+---------------+-------------------------------------------------------+

<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

+-------------------+--------------------------------+
|   **Attribute**   |           **Value**            |
+-------------------+--------------------------------+
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |
+-------------------+--------------------------------+

+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+
| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+
|                      variables                      |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |
+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+


<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

+---------------+---------------------+
| **Attribute** |      **Value**      |
+---------------+---------------------+
|  **extends**  |    ['.test:rules'   |
|               |  '.poetry:install'] |
+---------------+---------------------+

+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+
| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+
|                      variables                      |           POETRY_VIRTUALENVS_CREATE            |                      false                       |
+-----------------------------------------------------+------------------------------------------------+--------------------------------------------------+


<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

+---------------+---------------------------------------+
| **Attribute** |               **Value**               |
+---------------+---------------------------------------+
|   **image**   |             python:3.12.11            |
|   **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|   **stage**   |                 .post                 |
+---------------+---------------------------------------+

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

+-----------------+---------------------+
|  **Attribute**  |      **Value**      |
+-----------------+---------------------+
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |
+-----------------+---------------------+

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

+---------------+-------------------+
| **Attribute** |     **Value**     |
+---------------+-------------------+
|  **extends**  | ['.build:python'] |
+---------------+-------------------+

<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

+---------------+-------------------------------------------------+
| **Attribute** |                    **Value**                    |
+---------------+-------------------------------------------------+
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
+---------------+-------------------------------------------------+

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

+---------------+-------------------------------------------------+
| **Attribute** |                    **Value**                    |
+---------------+-------------------------------------------------+
|   **image**   |                  docker:latest                  |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
|  **services** |                 ['docker:dind']                 |
|   **stage**   |                      build                      |
|    **tags**   |              ['gitlab-org-docker']              |
+---------------+-------------------------------------------------+

[comment]: <> (gitlab-docs-closing-auto-generated)
