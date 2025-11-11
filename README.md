# Gitlab Docs

## 📖 Overview
GitLab Docs is your portable, Python-powered sidekick for keeping GitLab CI/CD pipelines well-documented.
If your system supports Python 3, you can install it instantly — no complex setup, no platform restrictions.

### 💡 Why it matters:

Code documentation is crucial.

Pipeline documentation is critical.

As pipelines grow, the what, when, and where of your workflows often get lost.

That’s where GitLab Docs comes in — a simple, elegant CLI tool that automatically generates and updates Markdown documentation for your pipelines, right alongside your code.

### ✨ Key Features
🛠 Portable — Works anywhere Python 3 runs.

📜 Markdown Output — Friendly for developers, perfect for GitLab README integration.

🔄 Auto-Update Mode — Insert or refresh documentation between customizable markers.

🧩 Multi-Block Support — Maintain different sections for different workflows.

🧪 Dry Run Mode — Preview changes without touching files.

### Python

```bash
pip3 install --user gitlab-docs
```

### Docker

```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```
or

```bash
podman run -it -v $(PWD):/gitlab-docs charlieasmith93/gitlab-docs
```

[comment]: <> (gitlab-docs-attribute-opening-auto-generated)


|    **File**    |   Job Name   |             image              |
| :------------: | :----------: | :----------------------------: |
| .gitlab-ci.yml |  megalinter  | oxsecurity/megalinter-ci_light |
| .gitlab-ci.yml | bump-version |         python:3.12.11         |
| .gitlab-ci.yml | docker-build |         docker:latest          |
[comment]: <> (gitlab-docs-attribute-closing-auto-generated)

[comment]: <> (gitlab-docs-opening-auto-generated)

# GITLAB DOCS - .gitlab-ci.yml

## Inputs

|    Key    |        Value        | Description | Options  | Expand |
| :-------: | :-----------------: | :---------: | :------: | :----: |
| job-stage | {'default': 'test'} |   &#x274c;  | &#x274c; |  true  |


## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| APPLICATION |  gitlab-docs   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |

## Jobs
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Attribute** |                       **Value**                       |
| :-----------: | :---------------------------------------------------: |
|   **rules**   |                ['if': '$CI_COMMIT_TAG'                |
|               |                     'when': 'never'                   |
|               |  'if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|               |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|   **stage**   |                          test                         |

<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|   **Attribute**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |


<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Attribute** |      **Value**      |
| :-----------: | :-----------------: |
|  **extends**  |    ['.test:rules'   |
|               |  '.poetry:install'] |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |           POETRY_VIRTUALENVS_CREATE            |                      false                       |


<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Attribute** |               **Value**               |
| :-----------: | :-----------------------------------: |
|   **image**   |             python:3.12.11            |
|   **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|   **stage**   |                publish                |

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|  **Attribute**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Attribute** |    **Value**     |
| :-----------: | :--------------: |
|  **extends**  | ['.build:python' |
|               |  '.test:rules']  |

<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Attribute**  |        **Value**         |
| :-------------: | :----------------------: |
|    **cache**    |            []            |
| **environment** |         release          |
|   **extends**   |   ['.poetry:install']    |
|    **rules**    | ['if': '$CI_COMMIT_TAG'] |
|    **stage**    |         publish          |

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Attribute** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|   **image**   |                  docker:latest                  |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
|  **services** |                 ['docker:dind']                 |
|   **stage**   |                      build                      |
|    **tags**   |              ['gitlab-org-docker']              |

[comment]: <> (gitlab-docs-closing-auto-generated)
