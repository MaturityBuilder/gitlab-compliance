# release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
Optionally outputs Markdown files.

## Usage

```
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

### `--token` (required)

- **Type:** `STRING`
- **Usage:** `--token`

GitLab personal access token

### `--url`

- **Type:** `STRING`
- **Default:** `https://gitlab.com`
- **Usage:** `--url`

GitLab instance URL

### `--projects` (required)

- **Type:** `STRING`
- **Usage:** `--projects`

List of GitLab project IDs or full paths

### `--since-tag`

- **Type:** `STRING`
- **Usage:** `--since-tag`

Baseline tag name (default: latest semver tag, else most recent by date)

### `--markdown`

- **Type:** `path`
- **Default:** `.`
- **Usage:** `--markdown`

Directory to output Markdown release notes

### `--no-write`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--no-write`

Skip writing Markdown files

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
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
