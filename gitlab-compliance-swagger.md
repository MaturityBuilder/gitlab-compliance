# GitLab pipeline reference — `.gitlab-ci.yml`

- **Config file:** `.gitlab-ci.yml`
- **Jobs:** 12

## Contents

- [Inputs](#inputs)
- [Variables](#variables)
- [Includes](#includes)
- [Jobs](#jobs) (12)
  - Image · (unset)
  - Image · oxsecurity/megalinter-ci_light@sha256:54e221da51b3fb959dfd4fc5e21920e0a0fa339ba68e0e9162b894a01a52ed34
  - Image · python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb57bd2d1c3f7ce
  - Image · docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515

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

### Image · (unset)

### TEMPLATE · .INSTALL_POETRY

> No attributes documented.

---

### TEMPLATE · .TEST:RULES

> stage: test

#### .TEST:RULES · attributes

| Attribute | Value |
| --------- | ----- |
| stage     | test  |

---

### JOB · BEHAVE-TESTS

> No attributes documented.

#### BEHAVE-TESTS · nested attributes

| Attribute | Key                       | Value |
| --------- | ------------------------- | ----- |
| variables | POETRY_VIRTUALENVS_CREATE | false |

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

> No attributes documented.

---

### TEMPLATE · .DOCS:ZENSICAL

> No attributes documented.

---

### JOB · DOCS:REVIEW

> stage: build

#### DOCS:REVIEW · attributes

| Attribute | Value |
| --------- | ----- |
| stage     | build |

---

### JOB · PAGES

> stage: publish

#### PAGES · attributes

| Attribute | Value   |
| --------- | ------- |
| stage     | publish |

---

### JOB · PUBLISH

> cache: [] · environment: release · stage: publish

#### PUBLISH · attributes

| Attribute   | Value   |
| ----------- | ------- |
| cache       | []      |
| environment | release |
| stage       | publish |

---

### Image · oxsecurity/megalinter-ci_light@sha256:54e221da51b3fb959dfd4fc5e21920e0a0fa339ba68e0e9162b894a01a52ed34

### JOB · MEGALINTER

> allow_failure: True · image: oxsecurity/megalinter-ci_light@sha256:54e221...

#### MEGALINTER · attributes

- **allow_failure:** `True`
- **image:**
  `oxsecurity/megalinter-ci_light@sha256:54e221da51b3fb959dfd4fc5e21920e0a0fa339ba68e0e9162b894a01a52ed34`

#### MEGALINTER · nested attributes

| Attribute | Key               | Value           |
| --------- | ----------------- | --------------- |
| variables | DEFAULT_WORKSPACE | $CI_PROJECT_DIR |

---

### Image · python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb57bd2d1c3f7ce

### JOB · BUMP-VERSION

> image: python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb5...

#### BUMP-VERSION · attributes

- **image:**
  `python@sha256:c1a5d356638cc86bd865d9019efbc34a6b0c3ad15a21e5ab4eb57bd2d1c3f7ce`
- **stage:** `publish`

---

### Image · docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515

### JOB · DOCKER-BUILD

> image: docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098...

#### DOCKER-BUILD · attributes

- **image:**
  `docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- **services:**
  `1. docker@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515`
- **stage:** `build`
- **tags:** `1. gitlab-org-docker`

---
