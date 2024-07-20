

## /gitlab-project/gitlab-ci/includes_without_keys.yml

| Include Type |             Project              | Version |         File        | Variables | Rules |
| :----------: | :------------------------------: | :-----: | :-----------------: | :-------: | :---: |
|   project    | charlieasmith/a-generic-fragment |   main  | a-fragment-file.yml |           |       |

## /gitlab-project/gitlab-ci/includes_with_keys.yml

| Include Type |             Project              | Version |         File        | Variables | Rules |
| :----------: | :------------------------------: | :-----: | :-----------------: | :-------: | :---: |
|   project    | charlieasmith/a-generic-fragment |   main  | a-fragment-file.yml |           |       |

## /gitlab-project/.gitlab-ci.yml

| Include Type |                   Project                    | Version |         File        |        Variables        |                         Rules                         |
| :----------: | :------------------------------------------: | :-----: | :-----------------: | :---------------------: | :---------------------------------------------------: |
|    local     |     gitlab-ci/includes_without_keys.yml      |   n/a   |                     |                         |                                                       |
|    local     |       gitlab-ci/includes_with_keys.yml       |   n/a   |                     | {'MY_VARIABLE': 'true'} | [{'if': '$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH'}] |
|  component   | https://gitlab.com/charlieasmith/gitlab-docs |   main  |                     |  {'MY_INPUTS': 'true'}  | [{'if': '$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH'}] |
|   project    |       charlieasmith/a-generic-fragment       |   main  | a-fragment-file.yml | {'MY_VARIABLE': 'true'} | [{'if': '$CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH'}] |