# release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
    Optionally outputs Markdown files.

## Usage

```text
Usage: gitlab-compliance release-notes [OPTIONS]
```

## Options

### `--token`

- **Name:** `token`
- **Kind:** Option
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** GitLab personal access token

### `--url`

- **Name:** `url`
- **Kind:** Option
- **Required:** no
- **Default:** `https://gitlab.com`
- **Type:** `STRING`
- **Description:** GitLab instance URL

### `--projects`

- **Name:** `projects`
- **Kind:** Option
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** List of GitLab project IDs or full paths

### `--since-tag`

- **Name:** `since_tag`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Baseline tag name (default: latest semver tag, else most recent by date)

### `--markdown`

- **Name:** `markdown_dir`
- **Kind:** Option
- **Required:** no
- **Default:** `.`
- **Type:** `<click.types.Path object at 0x7f8e088edc10>`
- **Description:** Directory to output Markdown release notes

### `--no-write`

- **Name:** `no_write`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Skip writing Markdown files


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
