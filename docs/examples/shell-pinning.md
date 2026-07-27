# Shell script dependency pinning

Supply-chain controls for packages and downloads inside GitLab CI job scripts.

## Policy pack

Packaged as [`shell-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/src/compliance/builtin_policies/shell/shell-pinning.feature)
with IDs `GLCI-SHELL-PIN-001` … `GLCI-SHELL-PIN-010`.

Examples of failures:

- `curl … | bash` (`GLCI-SHELL-PIN-002`)
- `apk add curl` without `curl=version` (`GLCI-SHELL-PIN-004`)
- `pip3 install requests` without `==` pinning (`GLCI-SHELL-PIN-003`)
- `yum install curl` / `dnf install curl` without a version segment
  (`GLCI-SHELL-PIN-010`)
- `docker pull nginx` or `docker run nginx` without a tag or digest (`GLCI-SHELL-PIN-009`)
- Download without nearby `sha256sum` (`GLCI-SHELL-PIN-001`)

## Run

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

Back to [Examples](index.md).
