# Installing via pip

`gitlab-compliance` is published on
[PyPI](https://pypi.org/project/gitlab-compliance/) as the `gitlab-compliance`
package.

It requires **Python 3.12**. Installation is standard:

```bash
python3.12 -m pip install --user gitlab-compliance
gitlab-compliance --help
```

Two CLI entry points are available:

| Command             | Status                                                 |
| ------------------- | ------------------------------------------------------ |
| `gitlab-compliance` | **Preferred** — compliance-first naming                |
| `gitlab-docs`       | **Deprecated** — same tool; shows a deprecation notice |

### Development install

From a clone of the repository:

```bash
poetry install
poetry run gitlab-compliance --help
```

### Virtual environment (recommended)

```bash
python3.12 -m venv venv
source venv/bin/activate
python -m pip install gitlab-compliance
gitlab-compliance check --help
```

Next: [Usage](../usage/index.md).
