# Pipeline documentation example

Sample `generate` output.

<!-- gitlab-compliance-opening-auto-generated -->
## GITLAB COMPLIANCE - .gitlab-ci.yml

## Inputs

|    Key    | Default | Description | Options  | Expand |
| :-------- | :------ | :---------- | :------- | :----- |
| job-stage | test    |   &#x274c;  | &#x274c; |  true  |

## Variables

| Key         | Value          | Description | Options   | Expand |
| ----------- | -------------- | ----------- | --------- | ------ |
| APPLICATION | gitlab-compliance    | _not set_   | _not set_ | true   |
| OUTPUT_FILE | GITLAB-COMPLIANCE.md | _not set_   | _not set_ | true   |

- **Rules # 1**
  - **if:** `$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH && $CI_COMMIT_MESSAGE =~ /^chore: bumping version to/`
  - **when:** `never`
- **Rules # 2**
  - **if:** `$CI_PIPELINE_SOURCE == "merge_request_event" || $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH || $CI_COMMIT_REF_NAME == $CI_COMMIT_TAG`

## Jobs

### TEMPLATE · .TEST:RULES

| **Attribute** | **Value** |
| ------------- | --------- |
| **stage**     | test      |

| Rule # | if                                           | when  |
| ------ | -------------------------------------------- | ----- |
| 1      | $CI_COMMIT_TAG                               | never |
| 2      | $CI_PIPELINE_SOURCE == "merge_request_event" |       |
| 3      | $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH      |       |

### JOB · MEGALINTER

- ****allow_failure**:** `True`
- ****extends**:** `1. .test:rules`
- ****image**:**
  `oxsecurity/megalinter-ci_light@sha256:54e221da51b3fb959dfd4fc5e21920e0a0fa339ba68e0e9162b894a01a52ed34`

- **Rule # 1**
  - **if:** `$CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH && $CI_COMMIT_BRANCH != $CI_COMMIT_TAG`

| **Attribute** | **Key**           | **Value**       |
| ------------- | ----------------- | --------------- |
| variables     | DEFAULT_WORKSPACE | $CI_PROJECT_DIR |

### JOB · BEHAVE-TESTS

| **Attribute** | **Value**      |
| ------------- | -------------- |
| **extends**   | 1. .test:rules |

| **Attribute** | **Key**                   | **Value** |
| ------------- | ------------------------- | --------- |
| variables     | POETRY_VIRTUALENVS_CREATE | false     |

### JOB · BUMP-VERSION

- ****image**:**
  `python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb57bd2d1c3f7ce`
- ****stage**:** `publish`

| Rule # | if                          |
| ------ | --------------------------- |
| 1      | $CI_COMMIT_BRANCH == "main" |

### TEMPLATE · .BUILD:PYTHON

| **Attribute**   | **Value** |
| --------------- | --------- |
| **environment** | release   |
| **stage**       | build     |

### JOB · TEST-BUILD

- ****extends**:**
  1. .build:python
  2. .test:rules

### JOB · DOCS:REVIEW

- ****extends**:**
  1. .docs:zensical
  2. .test:rules
- ****stage**:** `build`

### JOB · PAGES

| **Attribute** | **Value**      |
| ------------- | -------------- |
| **extends**   | .docs:zensical |
| **stage**     | publish        |

| Rule # | if                                      |
| ------ | --------------------------------------- |
| 1      | $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH |

### JOB · PUBLISH

| **Attribute**   | **Value** |
| --------------- | --------- |
| **cache**       | []        |
| **environment** | release   |
| **stage**       | publish   |

| Rule # | if             |
| ------ | -------------- |
| 1      | $CI_COMMIT_TAG |

### JOB · DOCKER-BUILD

- ****image**:**
  `docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- ****services**:**
  `1. docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- ****stage**:** `build`
- ****tags**:** `1. gitlab-org-docker`

| Rule # | if                                    |
| ------ | ------------------------------------- |
| 1      | $CI_COMMIT_REF_NAME != $CI_COMMIT_TAG |
<!-- gitlab-compliance-closing-auto-generated -->
