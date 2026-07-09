# release-notes

Generate release notes for GitLab projects and optionally write Markdown files.

## Usage

```text
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

| Parameter | Required | Type | Default | Usage | Description |
| --------- | -------- | ---- | ------- | ----- | ----------- |
| `token` | Yes | `text` | `None` | `--token` | GitLab personal access token. |
| `url` | No | `text` | `https://gitlab.com` | `--url` | GitLab instance URL. |
| `projects` | Yes | `text` | `None` | `--projects` | List of GitLab project IDs or full paths. |
| `since_tag` | No | `text` | `None` | `--since-tag` | Baseline tag name. Defaults to latest semver tag, then most recent by date. |
| `markdown_dir` | No | `path` | `.` | `--markdown` | Directory to output Markdown release notes. |
| `no_write` | No | `boolean` | `False` | `--no-write` | Skip writing Markdown files. |
| `help` | No | `boolean` | `False` | `--help` | Show this message and exit. |

## CLI Help

```text
Usage: gitlab-compliance release-notes [OPTIONS]

  Generate release notes for GitLab projects and optionally write Markdown
  files.

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
