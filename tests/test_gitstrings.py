from pathlib import Path

from click.testing import CliRunner

from src.gitlab_compliance import gitlab_compliance
from src.modules.common import format_description_cell
from src.modules.constants import (
    GITSTRINGS_MARKER_CLOSE,
    GITSTRINGS_MARKER_OPEN,
)
from src.modules.gitstrings import (
    extract_gitstrings_blocks,
    extract_gitstrings_blocks_from_ci_yaml,
    parse_directives,
    process_gitstrings,
    render_fragment,
    resolve_fragment_output,
)
from src.properties.table_render import render_inputs_table

MARKER_BLOCK = f"""{GITSTRINGS_MARKER_OPEN}
{GITSTRINGS_MARKER_CLOSE}
"""


def test_format_description_cell_multiline():
    assert format_description_cell("one line") == "one line"
    assert format_description_cell("a\nb") == "a<br>b"


def test_parse_directives_multiline_description():
    raw = """# @title Inputs
# @description
#   Line one
#   Line two
# @render inputs
spec:
  inputs:
    x: test
"""
    directives, cleaned = parse_directives(raw)
    assert directives.title == "Inputs"
    assert "Line one" in directives.description
    assert "Line two" in directives.description
    assert directives.render == "inputs"
    assert "spec:" in cleaned
    assert "# @title" not in cleaned


def test_extract_gitstrings_blocks_ignores_plain_yaml():
    md = """# Intro

```yaml
plain: true
```

```yaml gitstrings
# @render variables
variables:
  APP: my-app
```
"""
    blocks = extract_gitstrings_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].directives.render == "variables"


def test_extract_gitstrings_blocks_from_ci_yaml():
    ci = """---
# @title Inputs
# @render inputs
spec:
  inputs:
    x:
      default: a
---
# @title Vars
# @render variables
variables:
  APP: one
image:
  name: foo
"""
    blocks = extract_gitstrings_blocks_from_ci_yaml(ci)
    assert len(blocks) == 2
    assert blocks[0].directives.title == "Inputs"
    assert "spec:" in blocks[0].cleaned_yaml
    assert "image:" not in blocks[1].cleaned_yaml
    assert blocks[1].directives.render == "variables"


def test_process_gitstrings_from_gitlab_ci_yml(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    readme = tmp_path / "README.md"
    ci.write_text(
        """# @title Vars
# @render variables
# @output README.md
variables:
  Z: 9
stages:
  - test
""",
        encoding="utf-8",
    )
    readme.write_text(MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(ci, keep_source=False)
    text = readme.read_text(encoding="utf-8")
    assert "Z" in text
    assert "Source:" in text
    assert ".gitlab-ci.yml#L1-" in text


def test_source_link_uses_ci_repository_url_for_current_repo(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    git_dir = project / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    ci = project / ".gitlab-ci.yml"
    ci.write_text(
        """# @render variables
variables:
  Z: 9
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(project)
    monkeypatch.setenv(
        "CI_REPOSITORY_URL",
        "https://oauth2:secret@gitlab.com/example/current.git",
    )
    monkeypatch.setenv("CI_COMMIT_SHA", "abc123")

    block = extract_gitstrings_blocks_from_ci_yaml(ci.read_text(encoding="utf-8"))[0]
    out = render_fragment(block, keep_source=False, scan_path=ci)

    assert (
        "https://gitlab.com/example/current/-/blob/abc123/.gitlab-ci.yml#L1-3"
        in out
    )
    assert "secret" not in out


def test_source_link_uses_nested_repo_origin_over_current_ci_url(tmp_path, monkeypatch):
    current = tmp_path / "current"
    nested = current / "vendor" / "policy"
    nested.mkdir(parents=True)
    (current / ".git").mkdir()
    nested_git = nested / ".git"
    nested_git.mkdir()
    (nested_git / "HEAD").write_text("ref: refs/heads/release\n", encoding="utf-8")
    (nested_git / "config").write_text(
        '[remote "origin"]\n'
        "    url = git@gitlab.com:security/nested-policy.git\n",
        encoding="utf-8",
    )
    ci = nested / ".gitlab-ci.yml"
    ci.write_text(
        """# @render variables
variables:
  Z: 9
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(current)
    monkeypatch.setenv(
        "CI_REPOSITORY_URL",
        "https://gitlab.com/example/current.git",
    )

    block = extract_gitstrings_blocks_from_ci_yaml(ci.read_text(encoding="utf-8"))[0]
    out = render_fragment(block, keep_source=False, scan_path=ci)

    assert (
        "https://gitlab.com/security/nested-policy/-/blob/release/.gitlab-ci.yml#L1-3"
        in out
    )
    assert "example/current" not in out


def test_process_gitstrings_from_multi_document_gitlab_ci_yml(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    readme = tmp_path / "README.md"
    ci.write_text(
        """---
# @title Inputs
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
---
# @title Vars
# @render variables
variables:
  APP: gitlab-compliance
test:
  stage: test
  script:
    - pytest
""",
        encoding="utf-8",
    )
    readme.write_text(MARKER_BLOCK, encoding="utf-8")

    process_gitstrings(ci, keep_source=False)
    text = readme.read_text(encoding="utf-8")

    assert "job-stage" in text
    assert "APP" in text
    assert "gitlab-compliance" in text


def test_render_inputs_table_multiline_description():
    table = render_inputs_table(
        {
            "stage": {
                "default": "test",
                "description": "Line one\nLine two",
            }
        }
    )
    assert "Line one<br>Line two" in table
    assert "test" in table
    assert "Default" in table
    assert "| Value |" not in table
    assert "{'default'" not in table


def test_format_structured_cell_nested_object():
    from src.modules.common import format_structured_cell

    cell = format_structured_cell(
        {
            "default": "test",
            "description": "ignored in value column when split",
        }
    )
    assert cell == "test"
    nested = format_structured_cell(
        {"default": "test", "type": "string", "description": "x"}
    )
    assert "<table>" not in nested
    assert "<strong>default</strong>" in nested
    assert "<strong>type</strong>" in nested
    assert "<br>" in nested
    assert "description" not in nested


def test_render_fragment_block_description(tmp_path):
    block = extract_gitstrings_blocks(
        """```yaml gitstrings
# @description
#   Fragment prose here.
# @render variables
variables:
  APP: x
```
"""
    )[0]
    out = render_fragment(block, keep_source=False)
    assert "Fragment prose here." in out
    assert "|" in out


def test_process_gitstrings_updates_markers_only(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """# Handwritten intro

```yaml gitstrings
# @render variables
variables:
  APP: my-app
```

"""
        + MARKER_BLOCK
        + "\n# Footer\n",
        encoding="utf-8",
    )
    intro_before = "# Handwritten intro"
    process_gitstrings(readme, readme, keep_source=False)
    text = readme.read_text(encoding="utf-8")
    assert intro_before in text
    assert "# Footer" in text
    assert "APP" in text
    assert GITSTRINGS_MARKER_OPEN in text
    assert "my-app" in text.split(GITSTRINGS_MARKER_OPEN)[1]


def test_process_gitstrings_regenerate_idempotent_outside_markers(tmp_path):
    readme = tmp_path / "README.md"
    fence = """```yaml gitstrings
# @render variables
variables:
  APP: v1
```
"""
    readme.write_text(fence + "\n" + MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(readme, readme, keep_source=False)
    outside = readme.read_text(encoding="utf-8").split(GITSTRINGS_MARKER_OPEN)[0]
    process_gitstrings(readme, readme, keep_source=False)
    outside_after = readme.read_text(encoding="utf-8").split(GITSTRINGS_MARKER_OPEN)[0]
    assert outside == outside_after


def test_coexistence_with_generate_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """[comment]: <> (gitlab-compliance-opening-auto-generated)
PIPELINE_DOC
[comment]: <> (gitlab-compliance-closing-auto-generated)

```yaml gitstrings
# @render variables
variables:
  Z: 1
```

"""
        + MARKER_BLOCK,
        encoding="utf-8",
    )
    process_gitstrings(readme, readme, keep_source=False)
    text = readme.read_text(encoding="utf-8")
    assert "PIPELINE_DOC" in text
    assert "Z" in text.split(GITSTRINGS_MARKER_OPEN)[1]


def test_output_path_split_input_output(tmp_path):
    sources = tmp_path / "sources.md"
    out = tmp_path / "out.md"
    sources.write_text(
        """```yaml gitstrings
# @render variables
variables:
  APP: from-source
```
""",
        encoding="utf-8",
    )
    out.write_text(MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(sources, out, keep_source=False)
    assert "from-source" in out.read_text(encoding="utf-8")
    assert "gitstrings" not in sources.read_text(encoding="utf-8") or "APP" in sources.read_text(
        encoding="utf-8"
    )


def test_at_output_directive(tmp_path):
    scan = tmp_path / "scan.md"
    inputs_doc = tmp_path / "INPUTS.md"
    default_readme = tmp_path / "README.md"
    scan.write_text(
        MARKER_BLOCK
        + f"""
```yaml gitstrings
# @output INPUTS.md
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
```

```yaml gitstrings
# @render variables
variables:
  APP: x
```
""",
        encoding="utf-8",
    )
    inputs_doc.write_text(MARKER_BLOCK, encoding="utf-8")
    default_readme.write_text(MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(scan, keep_source=False)
    assert "job-stage" in inputs_doc.read_text(encoding="utf-8")
    assert "APP" in scan.read_text(encoding="utf-8").split(GITSTRINGS_MARKER_OPEN)[1]
    assert "APP" not in default_readme.read_text(encoding="utf-8").split(
        GITSTRINGS_MARKER_OPEN
    )[1]


def test_cli_output_overrides_fragment_output_directive(tmp_path):
    scan = tmp_path / "scan.md"
    inputs_doc = tmp_path / "INPUTS.md"
    default_readme = tmp_path / "README.md"
    scan.write_text(
        """```yaml gitstrings
# @output INPUTS.md
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
```

```yaml gitstrings
# @render variables
variables:
  APP: x
```
""",
        encoding="utf-8",
    )
    default_readme.write_text(MARKER_BLOCK, encoding="utf-8")
    inputs_doc.write_text(MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(scan, default_readme, keep_source=False)
    marker_body = default_readme.read_text(encoding="utf-8").split(
        GITSTRINGS_MARKER_OPEN
    )[1]
    assert "job-stage" in marker_body
    assert "APP" in marker_body
    assert "job-stage" not in inputs_doc.read_text(encoding="utf-8").split(
        GITSTRINGS_MARKER_OPEN
    )[1]


def test_render_jobs_table_uses_markdown_pipe_not_bullets():
    from src.properties.table_render import render_jobs_table

    md = render_jobs_table(
        {
            "my-job": {
                "extends": [".base", ".rules"],
                "stage": "test",
            }
        }
    )
    assert "| Attribute | Value |" in md or "|" in md
    assert "- **extends:**" not in md
    assert "1. .base" not in md


def test_gitstrings_markers_are_html_comments():
    assert GITSTRINGS_MARKER_OPEN.startswith("<!--")
    assert GITSTRINGS_MARKER_CLOSE.startswith("<!--")


def test_upgrade_legacy_gitstrings_markers(tmp_path):
    readme = tmp_path / "README.md"
    from src.modules.constants import (
        GITSTRINGS_MARKER_CLOSE_LEGACY,
        GITSTRINGS_MARKER_OPEN_LEGACY,
    )
    from src.modules.gitstrings import _upgrade_legacy_gitstrings_markers

    readme.write_text(
        f"{GITSTRINGS_MARKER_OPEN_LEGACY}\nold\n{GITSTRINGS_MARKER_CLOSE_LEGACY}\n",
        encoding="utf-8",
    )
    _upgrade_legacy_gitstrings_markers(readme)
    text = readme.read_text(encoding="utf-8")
    assert GITSTRINGS_MARKER_OPEN in text
    assert GITSTRINGS_MARKER_CLOSE in text
    assert GITSTRINGS_MARKER_CLOSE_LEGACY not in text


def test_cli_document_gitstrings(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """```yaml gitstrings
# @render variables
variables:
  CLI: ok
```
"""
        + MARKER_BLOCK,
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        [
            "document",
            "gitstrings",
            "-i",
            str(readme),
            "--no-keep-source",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "CLI" in readme.read_text(encoding="utf-8")


def test_resolve_fragment_output_relative_to_scan_dir(tmp_path):
    scan = tmp_path / "docs" / "scan.md"
    scan.parent.mkdir(parents=True)
    directives, _ = parse_directives("# @output ../README.md\nvariables: {}")
    target = resolve_fragment_output(directives, tmp_path / "default.md", scan)
    assert target == (tmp_path / "README.md").resolve()
    forced = resolve_fragment_output(
        directives,
        tmp_path / "forced.md",
        scan,
        honor_fragment_output=False,
    )
    assert forced == (tmp_path / "forced.md").resolve()


def test_ci_yaml_cli_output_overrides_at_output(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    out = tmp_path / "GITLAB-DOCS.md"
    ci.write_text(
        """# @render variables
# @output README.md
variables:
  Z: 9
""",
        encoding="utf-8",
    )
    out.write_text(MARKER_BLOCK, encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text(MARKER_BLOCK, encoding="utf-8")
    process_gitstrings(ci, out, keep_source=False)
    assert "Z" in out.read_text(encoding="utf-8")
    assert "Z" not in readme.read_text(encoding="utf-8").split(GITSTRINGS_MARKER_OPEN)[1]