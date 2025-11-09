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
## Using gitlab-docs

This will output the results in the current working directory to `GITLAB-DOCS.md` based on the `.gitlab-ci.yml` config. Noting it will also automatically try to detect and produce documentation for any include configurations as well.

```
gitlab-docs

```

## Command Reference

A command line tool to convert your gitlab-ci yml into markdown documentation.

### Usage

```
Usage: gitlab-docs [OPTIONS] COMMAND [ARGS]...
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `DRY_MODE`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-docs [OPTIONS] COMMAND [ARGS]...

  A command line tool to convert your gitlab-ci yml into markdown
  documentation.

Options:
  --detailed               Will include workflow and rules from jobs.
  -d, --dry-mode           If set will disable documentation from being
                           written

  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.

  --help                   Show this message and exit.

Commands:
  get-images
```

## Example of what's generated
<br><hr>

[comment]: <> (gitlab-docs-opening-auto-generated)

            <h1><span class="badge text-bg-primary">GITLAB DOCS - .gitlab-ci.yml</span></h1>


## Inputs

|     Key     |           Value           | Description | Options  | Expand |
| :---------: | :-----------------------: | :---------: | :------: | :----: |
|  job-stage  |    {'default': 'test'}    |   &#x274c;  | &#x274c; |  true  |
| environment | {'default': 'production'} |   &#x274c;  | &#x274c; |  true  |



## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| APPLICATION |  gitlab-docs   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |



## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">SPEC</span></h4>

<hr>

| **Property** |                **Value**                |
| :----------: | :-------------------------------------: |
|  **inputs**  |      'job-stage': 'default': 'test'     |
|              |  'environment': 'default': 'production' |


## .gitlab-ci.yml
<h4><span class="badge text-bg-info">VARIABLES</span></h4>

<hr>

|   **Property**  |   **Value**    |
| :-------------: | :------------: |
| **APPLICATION** |  gitlab-docs   |
| **OUTPUT_FILE** | GITLAB-DOCS.md |
<h4><span class="badge text-bg-info">DEFAULT</span></h4>

<hr>

| **Property** |   **Value**    |
| :----------: | :------------: |
|   **tags**   | ['gitlab-org'] |
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|  **stage**   |                          test                         |
<h4><span class="badge text-bg-info">WORKFLOW</span></h4>

<hr>

| **Property** |                       **Value**                       |
| :----------: | :---------------------------------------------------: |
|  **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|              |     'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'   |
|              |     'if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG']    |
<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|    **Property**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |              ['megalinter-reports']              |
|                   artifacts                    |                   expire_in                    |                      1 week                      |
|                   variables                    |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |

<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Property** |      **Value**      |
| :----------: | :-----------------: |
| **extends**  |    ['.test:rules'   |
|              |  '.poetry:install'] |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   variables                    |           POETRY_VIRTUALENVS_CREATE            |                      false                       |

<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Property** |               **Value**               |
| :----------: | :-----------------------------------: |
|  **image**   |             python:3.12.11            |
|  **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|  **stage**   |                 .post                 |
<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|   **Property**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

| <span class="badge text-bg-danger">Type</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :--------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                   artifacts                    |                      when                      |                      always                      |
|                   artifacts                    |                     paths                      |               ['./dist/*.tar.gz']                |
|                   artifacts                    |                   expire_in                    |                      1 hour                      |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Property** |     **Value**     |
| :----------: | :---------------: |
| **extends**  | ['.build:python'] |
<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Property** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |
<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Property** |                    **Value**                    |
| :----------: | :---------------------------------------------: |
|  **image**   |                  docker:latest                  |
|  **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
| **services** |                 ['docker:dind']                 |
|  **stage**   |                      build                      |
|   **tags**   |              ['gitlab-org-docker']              |


## {attribute} Report


## {attribute} Report


## {attribute} Report


## {attribute} Report


## {attribute} Report


## {attribute} Report


## {attribute} Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report


## Gitlab Attribute Report
[comment]: <> (gitlab-docs-closing-auto-generated)
