# Gitlab Docs
## How to install
Gitlab Docs is portable utility based in python so any system that supports python3 you will be able to install it.
### Python
```bash
pip3 install --user gitlab-docs
```

### Docker
```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```
### Precommit Hook
```yml

```
## .gitlab-ci.yml

|     Key     |    Value    | Description | Options  | Expand |
| :---------: | :---------: | :---------: | :------: | :----: |
| APPLICATION | gitlab-docs |   &#x274c;  | &#x274c; |  true  |

## .gitlab-ci.yml

|  Job Name  |                                                                                                                     Config                                                                                                                    |
| :--------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|   image    |                                                                                                                  python:3.12                                                                                                                  |
| megalinter | {'stage': 'code-quality', 'image': 'oxsecurity/megalinter-python:v8.0.0', 'script': ['true'], 'variables': {'DEFAULT_WORKSPACE': '$CI_PROJECT_DIR'}, 'artifacts': {'when': 'always', 'paths': ['megalinter-reports'], 'expire_in': '1 week'}} |
|   build    |   {'stage': 'build', 'needs': [], 'script': ['curl -sSL https://install.python-poetry.org | python3 -', 'export PATH="/root/.local/bin:$PATH"', 'poetry --version', 'poetry build', 'pip3 install -q $(ls ./dist/*.tar.gz)', 'gitlab-docs']}  |

[comment]: <> (gitlab-docs-closing-auto-generated)
