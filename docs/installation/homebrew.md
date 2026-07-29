# Installing via Homebrew

`gitlab-compliance` can be installed with [Homebrew](https://brew.sh/) from the
[MaturityBuilder/homebrew-gitlab-compliance](https://github.com/MaturityBuilder/homebrew-gitlab-compliance)
tap. The formula installs the published
[PyPI](https://pypi.org/project/gitlab-compliance/) package into an isolated
Python virtual environment.

Requires **Homebrew** and downloads **Python 3.12** (via Homebrew) if needed.

## Install

```bash
brew tap MaturityBuilder/gitlab-compliance
brew install gitlab-compliance
gitlab-compliance --help
```

Fully qualified install (same formula):

```bash
brew install MaturityBuilder/gitlab-compliance/gitlab-compliance
```

### Install a specific version

```bash
brew install MaturityBuilder/gitlab-compliance/gitlab-compliance@2.2.0
brew link --force gitlab-compliance@2.2.0
```

## Upgrade

```bash
brew update
brew upgrade gitlab-compliance
```

## Uninstall

```bash
brew uninstall gitlab-compliance
```

To remove the tap as well:

```bash
brew untap MaturityBuilder/gitlab-compliance
```

## Notes

- The Homebrew formula tracks **PyPI** only. After a `v*` tag publishes to
  PyPI, CI regenerates pins in
  [homebrew-gitlab-compliance](https://github.com/MaturityBuilder/homebrew-gitlab-compliance).
- Prefer `gitlab-compliance` over the legacy `gitlab-docs` entry point.

Next: [Usage](../usage/index.md).
