# release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag. Optionally outputs Markdown files.

## Usage

```text
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--token` | STRING | `required` | GitLab personal access token |
| `--url` | STRING | `https://gitlab.com` | GitLab instance URL |
| `--projects` | STRING | `required` | List of GitLab project IDs or full paths |
| `--since-tag` | STRING | `none` | Baseline tag name (default: latest semver tag, else most recent by date) |
| `--markdown` | <click.types.Path object at 0x7fe9c91e81a0> | `.` | Directory to output Markdown release notes |
| `--no-write` | BOOL | `false` | Skip writing Markdown files |
| `--help` | BOOL | `false` | Show this message and exit. |


## CLI Help

```text
Usage: gitlab-compliance release-notes [OPTIONS]

  Generate release notes for multiple GitLab projects based on commits since
  the last tag. Optionally outputs Markdown files.

Options:
  --token TEXT          GitLab personal access token  [required]
  --url TEXT            GitLab instance URL  [default: https://gitlab.com]
  --projects TEXT       List of GitLab project IDs or full paths  [required]
  --since-tag TEXT      Baseline tag name (default: latest semver tag, else
                        most recent by date)
  --markdown DIRECTORY  Directory to output Markdown release notes
  --no-write            Skip writing Markdown files
  --help                Show this message and exit.
```
