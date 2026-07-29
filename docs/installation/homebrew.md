# Installing via Homebrew

`gitlab-compliance` can be installed with [Homebrew](https://brew.sh/) from the
[MaturityBuilder/gitlab-compliance-homebrew](https://github.com/MaturityBuilder/gitlab-compliance-homebrew)
tap. The formula installs the published
[PyPI](https://pypi.org/project/gitlab-compliance/) package into an isolated
Python virtual environment.

Requires **Homebrew** and downloads **Python 3.12** (via Homebrew) if needed.

## Install

Because the tap repository is not named `homebrew-*`, tap it with the clone URL:

```bash
brew tap MaturityBuilder/gitlab-compliance-homebrew https://github.com/MaturityBuilder/gitlab-compliance-homebrew
brew install gitlab-compliance
gitlab-compliance --help
```

Fully qualified install (same formula):

```bash
brew install MaturityBuilder/gitlab-compliance-homebrew/gitlab-compliance
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
brew untap MaturityBuilder/gitlab-compliance-homebrew
```

## Notes

- The Homebrew formula tracks **PyPI** only. After a `v*` tag publishes to
  PyPI, CI regenerates pins in
  [gitlab-compliance-homebrew](https://github.com/MaturityBuilder/gitlab-compliance-homebrew).
- Prefer `gitlab-compliance` over the legacy `gitlab-docs` entry point.

Next: [Usage](../usage/index.md).
