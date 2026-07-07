# Command Reference
## gitlab-compliance

GitLab CI compliance and pipeline documentation.

Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API settings),
or generate Markdown/HTML documentation from pipeline YAML.

### Usage

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...
```

### Options
* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...

  GitLab CI compliance and pipeline documentation.

  Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API
  settings), or generate Markdown/HTML documentation from pipeline YAML.

Options:
  --help  Show this message and exit.

Commands:
  compliance       Run Gherkin compliance policies against GitLab CI YAML...
  compliance-doc   Generate a searchable policy catalog from...
  compliance-pull  Pull a compliance policy bundle from an OCI registry.
  compliance-push  Push a compliance policy bundle to an OCI registry...
  generate         Will scan through your gitlab-ci yml and build...
  get-attributes   Compared to the generate command, the get-attribute...
  release-notes    Generate release notes for multiple GitLab projects...
```


## gitlab-compliance get-attributes

Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
Args:
    OUTPUT_FILE (_type_): _description_
    GLDOCS_CONFIG_FILE (_type_): _description_
    attributes (_type_): _description_
    json (_type_): _description_

### Usage

```
Usage: gitlab-compliance get-attributes [OPTIONS]
```

### Options
* `attributes`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--attributes
-a`

  Pass a comma seperated list of gitlab ci yml attributes


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `json_format`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--json
-j`

  Return results in json format.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance get-attributes [OPTIONS]

  Compared to the generate command, the get-attribute command allows you to
  pass the properties you wish to document and produces a markdown table.
  Args:     OUTPUT_FILE (_type_): _description_     GLDOCS_CONFIG_FILE
  (_type_): _description_     attributes (_type_): _description_     json
  (_type_): _description_

Options:
  -a, --attributes TEXT    Pass a comma seperated list of gitlab ci yml
                           attributes
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  -j, --json BOOLEAN       Return results in json format.
  --help                   Show this message and exit.
```


## gitlab-compliance dumps

# Click-md
Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.

### Usage

```
Usage: gitlab-compliance dumps [OPTIONS]
```

### Options
* `base_module` (REQUIRED): 
  * Type: STRING 
  * Default: `src.gitlab_docs`
  * Usage: `--baseModule`

  The base command module path to import


* `base_command` (REQUIRED): 
  * Type: STRING 
  * Default: `gitlab_compliance`
  * Usage: `--baseCommand`

  The base command function to import


* `docs_path` (REQUIRED): 
  * Type: STRING 
  * Default: `docs/`
  * Usage: `--docsPath`

  The docs dir path to write the md files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance dumps [OPTIONS]

  # Click-md Create md files per each command, in format of `parent-command`,
  under the `--docsPath` directory.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```


## gitlab-compliance generate

Will scan through your gitlab-ci yml and build documentation from the yml.

### Usage

```
Usage: gitlab-compliance generate [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format
-f`

  Output format for generated documentation.


* `DRY_MODE`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Output location of the generated documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate [OPTIONS]

  Will scan through your gitlab-ci yml and build documentation from the yml.

Options:
  --detailed                    Will include workflow and rules from jobs.
  -f, --format [markdown|html]  Output format for generated documentation.
  -d, --dry-mode                If set will disable documentation from being
                                written
  -o, --output-file TEXT        Output location of the generated
                                documentation.
  -i, --input-config TEXT       The Gitlab CI Input configuration file to
                                generated documentation from.
  --help                        Show this message and exit.
```


## gitlab-compliance generate-html

Deprecated: use `generate --format html` instead.

### Usage

```
Usage: gitlab-compliance generate-html [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `gitlab-compliance.html`
  * Usage: `--output-file
-o`

  Output location of the HTML documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate-html [OPTIONS]

  (Deprecated) Deprecated: use `generate --format html` instead.

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  --help                   Show this message and exit.
```


## gitlab-compliance compliance

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

### Usage

```
Usage: gitlab-compliance compliance [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).


* `pipeline_file`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.


* `output_format`: 
  * Type: Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality']) 
  * Default: `console`
  * Usage: `--format`

  Output format for the compliance report.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write rendered report to this file (markdown, html, mr-comment).


* `include_nested`: 
  * Type: BOOL 
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the compliance stash.


* `gitlab_url`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).


* `token`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).


* `project`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--project`

  GitLab project path or ID for API-backed policy checks.


* `group`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--group`

  GitLab group path or ID for API-backed policy checks.


* `strict`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--strict`

  Fail API-backed scenarios when connection info is missing (default: skip).


* `update`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--update`

  Pull the latest policies from an OCI registry before running checks.


* `policy_cache_dir`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--policy-cache-dir`

  Directory used when pulling OCI policy bundles (default: system temp).


* `dry_run`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-run`

  Parse and list scenarios without asserting.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance [OPTIONS]

  Run Gherkin compliance policies against GitLab CI YAML and optional API
  settings.

Options:
  -f, --features TEXT             Directory containing compliance policy
                                  .feature files or an OCI reference
                                  (oci://registry.example.com/policies:1.0.0).
                                  [required]
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the compliance report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --project TEXT                  GitLab project path or ID for API-backed
                                  policy checks.
  --group TEXT                    GitLab group path or ID for API-backed
                                  policy checks.
  --strict                        Fail API-backed scenarios when connection
                                  info is missing (default: skip).
  --update                        Pull the latest policies from an OCI
                                  registry before running checks.
  --policy-cache-dir TEXT         Directory used when pulling OCI policy
                                  bundles (default: system temp).
  --dry-run                       Parse and list scenarios without asserting.
  --help                          Show this message and exit.
```


## gitlab-compliance compliance-doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

### Usage

```
Usage: gitlab-compliance compliance-doc [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format`

  Output format for the policy catalog.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write the policy catalog to this file.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-doc [OPTIONS]

  Generate a searchable policy catalog from Conftest-style # METADATA
  annotations.

Options:
  -f, --features TEXT       Directory containing compliance policy .feature
                            files.  [required]
  --format [markdown|html]  Output format for the policy catalog.
  -o, --output-file TEXT    Write the policy catalog to this file.
  --help                    Show this message and exit.
```


## gitlab-compliance compliance-push

Push a compliance policy bundle to an OCI registry (Conftest-style).

### Usage

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files to publish.


* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```


## gitlab-compliance compliance-pull

Pull a compliance policy bundle from an OCI registry.

### Usage

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET
```

### Options
* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `output_dir`: 
  * Type: STRING 
  * Default: `policy`
  * Usage: `--output-dir
-o`

  Directory to extract pulled policies into.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```


## gitlab-compliance release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
Optionally outputs Markdown files.

### Usage

```
Usage: gitlab-compliance release-notes [OPTIONS]
```

### Options
* `token` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab personal access token


* `url`: 
  * Type: STRING 
  * Default: `https://gitlab.com`
  * Usage: `--url`

  GitLab instance URL


* `projects` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--projects`

  List of GitLab project IDs or full paths


* `since_tag`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--since-tag`

  Baseline tag name (default: latest semver tag, else most recent by date)


* `markdown_dir`: 
  * Type: <click.types.Path object at 0x727a0f461040> 
  * Default: `.`
  * Usage: `--markdown`

  Directory to output Markdown release notes


* `no_write`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--no-write`

  Skip writing Markdown files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

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


## gitlab-compliance

GitLab CI compliance and pipeline documentation.

Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API settings),
or generate Markdown/HTML documentation from pipeline YAML.

### Usage

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...
```

### Options
* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...

  GitLab CI compliance and pipeline documentation.

  Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API
  settings), or generate Markdown/HTML documentation from pipeline YAML.

Options:
  --help  Show this message and exit.

Commands:
  compliance       Run Gherkin compliance policies against GitLab CI YAML...
  compliance-doc   Generate a searchable policy catalog from...
  compliance-pull  Pull a compliance policy bundle from an OCI registry.
  compliance-push  Push a compliance policy bundle to an OCI registry...
  generate         Will scan through your gitlab-ci yml and build...
  get-attributes   Compared to the generate command, the get-attribute...
  release-notes    Generate release notes for multiple GitLab projects...
```


## gitlab-compliance get-attributes

Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
Args:
    OUTPUT_FILE (_type_): _description_
    GLDOCS_CONFIG_FILE (_type_): _description_
    attributes (_type_): _description_
    json (_type_): _description_

### Usage

```
Usage: gitlab-compliance get-attributes [OPTIONS]
```

### Options
* `attributes`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--attributes
-a`

  Pass a comma seperated list of gitlab ci yml attributes


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `json_format`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--json
-j`

  Return results in json format.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance get-attributes [OPTIONS]

  Compared to the generate command, the get-attribute command allows you to
  pass the properties you wish to document and produces a markdown table.
  Args:     OUTPUT_FILE (_type_): _description_     GLDOCS_CONFIG_FILE
  (_type_): _description_     attributes (_type_): _description_     json
  (_type_): _description_

Options:
  -a, --attributes TEXT    Pass a comma seperated list of gitlab ci yml
                           attributes
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  -j, --json BOOLEAN       Return results in json format.
  --help                   Show this message and exit.
```


## gitlab-compliance dumps

# Click-md
Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.

### Usage

```
Usage: gitlab-compliance dumps [OPTIONS]
```

### Options
* `base_module` (REQUIRED): 
  * Type: STRING 
  * Default: `src.gitlab_docs`
  * Usage: `--baseModule`

  The base command module path to import


* `base_command` (REQUIRED): 
  * Type: STRING 
  * Default: `gitlab_compliance`
  * Usage: `--baseCommand`

  The base command function to import


* `docs_path` (REQUIRED): 
  * Type: STRING 
  * Default: `docs/`
  * Usage: `--docsPath`

  The docs dir path to write the md files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance dumps [OPTIONS]

  # Click-md Create md files per each command, in format of `parent-command`,
  under the `--docsPath` directory.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```


## gitlab-compliance generate

Will scan through your gitlab-ci yml and build documentation from the yml.

### Usage

```
Usage: gitlab-compliance generate [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format
-f`

  Output format for generated documentation.


* `DRY_MODE`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Output location of the generated documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate [OPTIONS]

  Will scan through your gitlab-ci yml and build documentation from the yml.

Options:
  --detailed                    Will include workflow and rules from jobs.
  -f, --format [markdown|html]  Output format for generated documentation.
  -d, --dry-mode                If set will disable documentation from being
                                written
  -o, --output-file TEXT        Output location of the generated
                                documentation.
  -i, --input-config TEXT       The Gitlab CI Input configuration file to
                                generated documentation from.
  --help                        Show this message and exit.
```


## gitlab-compliance generate-html

Deprecated: use `generate --format html` instead.

### Usage

```
Usage: gitlab-compliance generate-html [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `gitlab-compliance.html`
  * Usage: `--output-file
-o`

  Output location of the HTML documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate-html [OPTIONS]

  (Deprecated) Deprecated: use `generate --format html` instead.

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  --help                   Show this message and exit.
```


## gitlab-compliance compliance

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

### Usage

```
Usage: gitlab-compliance compliance [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).


* `pipeline_file`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.


* `output_format`: 
  * Type: Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality']) 
  * Default: `console`
  * Usage: `--format`

  Output format for the compliance report.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write rendered report to this file (markdown, html, mr-comment).


* `include_nested`: 
  * Type: BOOL 
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the compliance stash.


* `gitlab_url`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).


* `token`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).


* `project`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--project`

  GitLab project path or ID for API-backed policy checks.


* `group`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--group`

  GitLab group path or ID for API-backed policy checks.


* `strict`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--strict`

  Fail API-backed scenarios when connection info is missing (default: skip).


* `update`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--update`

  Pull the latest policies from an OCI registry before running checks.


* `policy_cache_dir`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--policy-cache-dir`

  Directory used when pulling OCI policy bundles (default: system temp).


* `dry_run`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-run`

  Parse and list scenarios without asserting.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance [OPTIONS]

  Run Gherkin compliance policies against GitLab CI YAML and optional API
  settings.

Options:
  -f, --features TEXT             Directory containing compliance policy
                                  .feature files or an OCI reference
                                  (oci://registry.example.com/policies:1.0.0).
                                  [required]
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the compliance report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --project TEXT                  GitLab project path or ID for API-backed
                                  policy checks.
  --group TEXT                    GitLab group path or ID for API-backed
                                  policy checks.
  --strict                        Fail API-backed scenarios when connection
                                  info is missing (default: skip).
  --update                        Pull the latest policies from an OCI
                                  registry before running checks.
  --policy-cache-dir TEXT         Directory used when pulling OCI policy
                                  bundles (default: system temp).
  --dry-run                       Parse and list scenarios without asserting.
  --help                          Show this message and exit.
```


## gitlab-compliance compliance-doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

### Usage

```
Usage: gitlab-compliance compliance-doc [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format`

  Output format for the policy catalog.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write the policy catalog to this file.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-doc [OPTIONS]

  Generate a searchable policy catalog from Conftest-style # METADATA
  annotations.

Options:
  -f, --features TEXT       Directory containing compliance policy .feature
                            files.  [required]
  --format [markdown|html]  Output format for the policy catalog.
  -o, --output-file TEXT    Write the policy catalog to this file.
  --help                    Show this message and exit.
```


## gitlab-compliance compliance-push

Push a compliance policy bundle to an OCI registry (Conftest-style).

### Usage

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files to publish.


* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```


## gitlab-compliance compliance-pull

Pull a compliance policy bundle from an OCI registry.

### Usage

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET
```

### Options
* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `output_dir`: 
  * Type: STRING 
  * Default: `policy`
  * Usage: `--output-dir
-o`

  Directory to extract pulled policies into.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```


## gitlab-compliance release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
Optionally outputs Markdown files.

### Usage

```
Usage: gitlab-compliance release-notes [OPTIONS]
```

### Options
* `token` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab personal access token


* `url`: 
  * Type: STRING 
  * Default: `https://gitlab.com`
  * Usage: `--url`

  GitLab instance URL


* `projects` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--projects`

  List of GitLab project IDs or full paths


* `since_tag`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--since-tag`

  Baseline tag name (default: latest semver tag, else most recent by date)


* `markdown_dir`: 
  * Type: <click.types.Path object at 0x7c762baed760> 
  * Default: `.`
  * Usage: `--markdown`

  Directory to output Markdown release notes


* `no_write`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--no-write`

  Skip writing Markdown files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

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


## gitlab-compliance

GitLab CI compliance and pipeline documentation.

Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API settings),
or generate Markdown/HTML documentation from pipeline YAML.

### Usage

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...
```

### Options
* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance [OPTIONS] COMMAND [ARGS]...

  GitLab CI compliance and pipeline documentation.

  Run Gherkin policies against .gitlab-ci.yml (and optional GitLab API
  settings), or generate Markdown/HTML documentation from pipeline YAML.

Options:
  --help  Show this message and exit.

Commands:
  compliance       Run Gherkin compliance policies against GitLab CI YAML...
  compliance-doc   Generate a searchable policy catalog from...
  compliance-pull  Pull a compliance policy bundle from an OCI registry.
  compliance-push  Push a compliance policy bundle to an OCI registry...
  generate         Will scan through your gitlab-ci yml and build...
  get-attributes   Compared to the generate command, the get-attribute...
  release-notes    Generate release notes for multiple GitLab projects...
```


## gitlab-compliance get-attributes

Compared to the generate command, the get-attribute command allows you to pass the properties you wish to document and produces a markdown table.
Args:
    OUTPUT_FILE (_type_): _description_
    GLDOCS_CONFIG_FILE (_type_): _description_
    attributes (_type_): _description_
    json (_type_): _description_

### Usage

```
Usage: gitlab-compliance get-attributes [OPTIONS]
```

### Options
* `attributes`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--attributes
-a`

  Pass a comma seperated list of gitlab ci yml attributes


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `readme.md`
  * Usage: `--output-file
-o`

  Output location of the markdown documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `json_format`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--json
-j`

  Return results in json format.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance get-attributes [OPTIONS]

  Compared to the generate command, the get-attribute command allows you to
  pass the properties you wish to document and produces a markdown table.
  Args:     OUTPUT_FILE (_type_): _description_     GLDOCS_CONFIG_FILE
  (_type_): _description_     attributes (_type_): _description_     json
  (_type_): _description_

Options:
  -a, --attributes TEXT    Pass a comma seperated list of gitlab ci yml
                           attributes
  -o, --output-file TEXT   Output location of the markdown documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  -j, --json BOOLEAN       Return results in json format.
  --help                   Show this message and exit.
```


## gitlab-compliance dumps

# Click-md
Create md files per each command, in format of `parent-command`, under the `--docsPath` directory.

### Usage

```
Usage: gitlab-compliance dumps [OPTIONS]
```

### Options
* `base_module` (REQUIRED): 
  * Type: STRING 
  * Default: `src.gitlab_docs`
  * Usage: `--baseModule`

  The base command module path to import


* `base_command` (REQUIRED): 
  * Type: STRING 
  * Default: `gitlab_compliance`
  * Usage: `--baseCommand`

  The base command function to import


* `docs_path` (REQUIRED): 
  * Type: STRING 
  * Default: `docs/`
  * Usage: `--docsPath`

  The docs dir path to write the md files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance dumps [OPTIONS]

  # Click-md Create md files per each command, in format of `parent-command`,
  under the `--docsPath` directory.

Options:
  --baseModule TEXT   The base command module path to import  [required]
  --baseCommand TEXT  The base command function to import  [required]
  --docsPath TEXT     The docs dir path to write the md files  [required]
  --help              Show this message and exit.
```


## gitlab-compliance generate

Will scan through your gitlab-ci yml and build documentation from the yml.

### Usage

```
Usage: gitlab-compliance generate [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format
-f`

  Output format for generated documentation.


* `DRY_MODE`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-mode
-d`

  If set will disable documentation from being written


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Output location of the generated documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate [OPTIONS]

  Will scan through your gitlab-ci yml and build documentation from the yml.

Options:
  --detailed                    Will include workflow and rules from jobs.
  -f, --format [markdown|html]  Output format for generated documentation.
  -d, --dry-mode                If set will disable documentation from being
                                written
  -o, --output-file TEXT        Output location of the generated
                                documentation.
  -i, --input-config TEXT       The Gitlab CI Input configuration file to
                                generated documentation from.
  --help                        Show this message and exit.
```


## gitlab-compliance generate-html

Deprecated: use `generate --format html` instead.

### Usage

```
Usage: gitlab-compliance generate-html [OPTIONS]
```

### Options
* `detailed`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--detailed`

  Will include workflow and rules from jobs.


* `OUTPUT_FILE`: 
  * Type: STRING 
  * Default: `gitlab-compliance.html`
  * Usage: `--output-file
-o`

  Output location of the HTML documentation.


* `GLDOCS_CONFIG_FILE`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--input-config
-i`

  The Gitlab CI Input configuration file to generated documentation from.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance generate-html [OPTIONS]

  (Deprecated) Deprecated: use `generate --format html` instead.

Options:
  --detailed               Will include workflow and rules from jobs.
  -o, --output-file TEXT   Output location of the HTML documentation.
  -i, --input-config TEXT  The Gitlab CI Input configuration file to generated
                           documentation from.
  --help                   Show this message and exit.
```


## gitlab-compliance compliance

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

### Usage

```
Usage: gitlab-compliance compliance [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).


* `pipeline_file`: 
  * Type: STRING 
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.


* `output_format`: 
  * Type: Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality']) 
  * Default: `console`
  * Usage: `--format`

  Output format for the compliance report.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write rendered report to this file (markdown, html, mr-comment).


* `include_nested`: 
  * Type: BOOL 
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the compliance stash.


* `gitlab_url`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).


* `token`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).


* `project`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--project`

  GitLab project path or ID for API-backed policy checks.


* `group`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--group`

  GitLab group path or ID for API-backed policy checks.


* `strict`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--strict`

  Fail API-backed scenarios when connection info is missing (default: skip).


* `update`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--update`

  Pull the latest policies from an OCI registry before running checks.


* `policy_cache_dir`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--policy-cache-dir`

  Directory used when pulling OCI policy bundles (default: system temp).


* `dry_run`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--dry-run`

  Parse and list scenarios without asserting.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance [OPTIONS]

  Run Gherkin compliance policies against GitLab CI YAML and optional API
  settings.

Options:
  -f, --features TEXT             Directory containing compliance policy
                                  .feature files or an OCI reference
                                  (oci://registry.example.com/policies:1.0.0).
                                  [required]
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the compliance report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --project TEXT                  GitLab project path or ID for API-backed
                                  policy checks.
  --group TEXT                    GitLab group path or ID for API-backed
                                  policy checks.
  --strict                        Fail API-backed scenarios when connection
                                  info is missing (default: skip).
  --update                        Pull the latest policies from an OCI
                                  registry before running checks.
  --policy-cache-dir TEXT         Directory used when pulling OCI policy
                                  bundles (default: system temp).
  --dry-run                       Parse and list scenarios without asserting.
  --help                          Show this message and exit.
```


## gitlab-compliance compliance-doc

Generate a searchable policy catalog from Conftest-style # METADATA annotations.

### Usage

```
Usage: gitlab-compliance compliance-doc [OPTIONS]
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files.


* `output_format`: 
  * Type: Choice(['markdown', 'html']) 
  * Default: `markdown`
  * Usage: `--format`

  Output format for the policy catalog.


* `output_file`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--output-file
-o`

  Write the policy catalog to this file.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-doc [OPTIONS]

  Generate a searchable policy catalog from Conftest-style # METADATA
  annotations.

Options:
  -f, --features TEXT       Directory containing compliance policy .feature
                            files.  [required]
  --format [markdown|html]  Output format for the policy catalog.
  -o, --output-file TEXT    Write the policy catalog to this file.
  --help                    Show this message and exit.
```


## gitlab-compliance compliance-push

Push a compliance policy bundle to an OCI registry (Conftest-style).

### Usage

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET
```

### Options
* `features_dir` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files to publish.


* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```


## gitlab-compliance compliance-pull

Pull a compliance policy bundle from an OCI registry.

### Usage

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET
```

### Options
* `target` (REQUIRED) [argument]: 
  * Type: STRING 
  * Default: `none`
  * Usage: `target`

  


* `output_dir`: 
  * Type: STRING 
  * Default: `policy`
  * Usage: `--output-dir
-o`

  Directory to extract pulled policies into.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

```
Usage: gitlab-compliance compliance-pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```


## gitlab-compliance release-notes

Generate release notes for multiple GitLab projects based on commits since the last tag.
Optionally outputs Markdown files.

### Usage

```
Usage: gitlab-compliance release-notes [OPTIONS]
```

### Options
* `token` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--token`

  GitLab personal access token


* `url`: 
  * Type: STRING 
  * Default: `https://gitlab.com`
  * Usage: `--url`

  GitLab instance URL


* `projects` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--projects`

  List of GitLab project IDs or full paths


* `since_tag`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--since-tag`

  Baseline tag name (default: latest semver tag, else most recent by date)


* `markdown_dir`: 
  * Type: <click.types.Path object at 0x7e2a3543d880> 
  * Default: `.`
  * Usage: `--markdown`

  Directory to output Markdown release notes


* `no_write`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--no-write`

  Skip writing Markdown files


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



### CLI Help

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

