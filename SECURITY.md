# Security policy

## Supported versions

Security fixes are provided for the latest release on
[PyPI](https://pypi.org/project/gitlab-compliance/) and the `main` branch of
[this repository](https://github.com/MaturityBuilder/gitlab-compliance).

| Version | Supported |
| ------- | --------- |
| Latest PyPI release | Yes |
| `main` | Yes |
| Older releases | Best effort |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report sensitive issues by email to **me@charlieasmith.co.uk** with:

- A description of the issue and impact
- Steps to reproduce (proof-of-concept if available)
- Affected versions or commit SHA

We aim to acknowledge reports within **5 business days** and will coordinate
disclosure and a fix before public details when appropriate.

## Secure use

- Treat `GITLAB_TOKEN` and similar credentials as secrets; use masked CI
  variables and least-privilege project access tokens.
- See [API hardening examples](https://maturitybuilder.github.io/gitlab-compliance/examples/api-hardening/)
  in the documentation for policy patterns around CI variables.
