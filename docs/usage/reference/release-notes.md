# release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
    Optionally outputs Markdown files.

## Usage

```text
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `token` | text | yes | _not set_ | `--token` | GitLab personal access token |
| `url` | text | no | `https://gitlab.com` | `--url` | GitLab instance URL |
| `projects` | text | yes | _not set_ | `--projects` | List of GitLab project IDs or full paths |
| `since_tag` | text | no | `none` | `--since-tag` | Baseline tag name (default: latest semver tag, else most recent by date) |
| `markdown_dir` | directory | no | `.` | `--markdown` | Directory to output Markdown release notes |
| `no_write` | boolean | no | `false` | `--no-write` | Skip writing Markdown files |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

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
