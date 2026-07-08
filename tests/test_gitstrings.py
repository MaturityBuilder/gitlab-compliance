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
    assert "Z" in readme.read_text(encoding="utf-8")


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
        f"""```yaml gitstrings
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
    assert "job-stage" in inputs_doc.read_text(encoding="utf-8")
    assert "APP" in default_readme.read_text(encoding="utf-8")


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