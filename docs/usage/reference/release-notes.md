# release-notes

Generate release notes for GitLab projects, optionally as Markdown files.

## Usage

```text
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

- `token` (required)
  - Type: text
  - Default: _required_
  - Usage: `--token`

  GitLab personal access token

- `url`
  - Type: text
  - Default: `https://gitlab.com`
  - Usage: `--url`

  GitLab instance URL

- `projects` (required)
  - Type: text
  - Default: _required_
  - Usage: `--projects`

  List of GitLab project IDs or full paths

- `since_tag`
  - Type: text
  - Default: _not set_
  - Usage: `--since-tag`

  Baseline tag name (default: latest semver tag, else most recent by date)

- `markdown_dir`
  - Type: directory
  - Default: `.`
  - Usage: `--markdown`

  Directory to output Markdown release notes

- `no_write`
  - Type: boolean
  - Default: `false`
  - Usage: `--no-write`

  Skip writing Markdown files

- `help`
  - Type: boolean
  - Default: `false`
  - Usage: `--help`

  Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance release-notes [OPTIONS]

  Generate release notes for GitLab projects, optionally as Markdown files.

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
