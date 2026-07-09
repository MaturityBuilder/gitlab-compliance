# GitLab pipeline reference — `.gitlab-ci.yml`

- **Config file:** `.gitlab-ci.yml`
- **Jobs:** 12

## Contents

- [Inputs](#inputs)
- [Variables](#variables)
- [Includes](#includes)
- [Jobs](#jobs) (12)
  - .INSTALL_POETRY
  - .TEST:RULES
  - MEGALINTER
  - BEHAVE-TESTS
  - BUMP-VERSION
  - .BUILD:PYTHON
  - TEST-BUILD
  - .DOCS:ZENSICAL
  - DOCS:REVIEW
  - PAGES
  - PUBLISH
  - DOCKER-BUILD

## Inputs

| Key       | Value               | Description | Options | Expand |
| --------- | ------------------- | ----------- | ------- | ------ |
| job-stage | {'default': 'test'} |             |         | True   |

## Variables

| Key         | Value          | Description | Options | Expand |
| ----------- | -------------- | ----------- | ------- | ------ |
| APPLICATION | gitlab-docs    |             |         | True   |
| OUTPUT_FILE | GITLAB-DOCS.md |             |         | True   |

## Includes

- **local:** `gitlab-ci/hidden.jobs.yml`
  - **version:** `n/a`
  - **valid:** yes

- **project:** `charlieasmith/cas-cli`
  - **version:** `0.0.1`
  - **valid:** yes
  - **file:** `gitlab-include-sample.yml`

- **component:** `https://gitlab.com/charlieasmith/gitlab-docs`
  - **version:** `main`
  - **valid:** no
  - **variables:** `MY_INPUTS: true`
  - **rules:** `Rule 1: if=$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH`

- **component:** `https://gitlab.com/charlieasmith/gitlab-docs`
  - **version:** `1.0.0`
  - **valid:** yes
  - **variables:** `MY_INPUTS: true`
  - **rules:** `Rule 1: if=$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH`

## Jobs

### TEMPLATE · .INSTALL_POETRY

> No attributes documented.

---

### TEMPLATE · .TEST:RULES

> stage: test

#### .TEST:RULES · attributes

| Attribute | Value |
| --------- | ----- |
| stage     | test  |

#### .TEST:RULES · rules

| Rule # | if                                           | when  |
| ------ | -------------------------------------------- | ----- |
| 1      | $CI_COMMIT_TAG                               | never |
| 2      | $CI_PIPELINE_SOURCE == "merge_request_event" |       |
| 3      | $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH      |       |

---

### JOB · MEGALINTER

> allow_failure: True · extends: 1. .test:rules · image: oxsecurity/megalin...

#### MEGALINTER · attributes

- **allow_failure:** `True`
- **extends:** `1. .test:rules`
- **image:**
  `oxsecurity/megalinter-ci_light@sha256:54e221da51b3fb959dfd4fc5e21920e0a0fa339ba68e0e9162b894a01a52ed34`

#### MEGALINTER · rules

- **Rule # 1**
  - **if:** `$CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH && $CI_COMMIT_BRANCH != $CI_COMMIT_TAG`

#### MEGALINTER · nested attributes

| Attribute | Key               | Value           |
| --------- | ----------------- | --------------- |
| variables | DEFAULT_WORKSPACE | $CI_PROJECT_DIR |

---

### JOB · BEHAVE-TESTS

> extends: 1. .test:rules

#### BEHAVE-TESTS · attributes

| Attribute | Value          |
| --------- | -------------- |
| extends   | 1. .test:rules |

#### BEHAVE-TESTS · nested attributes

| Attribute | Key                       | Value |
| --------- | ------------------------- | ----- |
| variables | POETRY_VIRTUALENVS_CREATE | false |

---

### JOB · BUMP-VERSION

> image: python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb5...

#### BUMP-VERSION · attributes

- **image:**
  `python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb57bd2d1c3f7ce`
- **stage:** `publish`

#### BUMP-VERSION · rules

| Rule # | if                          |
| ------ | --------------------------- |
| 1      | $CI_COMMIT_BRANCH == "main" |

---

### TEMPLATE · .BUILD:PYTHON

> environment: release · stage: build

#### .BUILD:PYTHON · attributes

| Attribute   | Value   |
| ----------- | ------- |
| environment | release |
| stage       | build   |

---

### JOB · TEST-BUILD

> extends: 1. .build:python

1. .test:rules

#### TEST-BUILD · attributes

- **extends:**
  1. .build:python
  2. .test:rules

---

### TEMPLATE · .DOCS:ZENSICAL

> No attributes documented.

---

### JOB · DOCS:REVIEW

> extends: 1. .docs:zensical

1. .test:rules · stage: build

#### DOCS:REVIEW · attributes

- **extends:**
  1. .docs:zensical
  2. .test:rules
- **stage:** `build`

---

### JOB · PAGES

> extends: .docs:zensical · stage: publish

#### PAGES · attributes

| Attribute | Value          |
| --------- | -------------- |
| extends   | .docs:zensical |
| stage     | publish        |

#### PAGES · rules

| Rule # | if                                      |
| ------ | --------------------------------------- |
| 1      | $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH |

---

### JOB · PUBLISH

> cache: [] · environment: release · stage: publish

#### PUBLISH · attributes

| Attribute   | Value   |
| ----------- | ------- |
| cache       | []      |
| environment | release |
| stage       | publish |

#### PUBLISH · rules

| Rule # | if             |
| ------ | -------------- |
| 1      | $CI_COMMIT_TAG |

---

### JOB · DOCKER-BUILD

> image: docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098...

#### DOCKER-BUILD · attributes

- **image:**
  `docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- **services:**
  `1. docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- **stage:** `build`
- **tags:** `1. gitlab-org-docker`

#### DOCKER-BUILD · rules

| Rule # | if                                    |
| ------ | ------------------------------------- |
| 1      | $CI_COMMIT_REF_NAME != $CI_COMMIT_TAG |

---
