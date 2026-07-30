# Nested 10-hop shell-check fixtures

Template fixtures for happy/sad shell-check runs through a linear
`include: local:` chain.

## Depth model

| Hop | File |
| --- | --- |
| 0 | `{happy,sad}/.gitlab-ci.yml` |
| 1–10 | `{happy,sad}/layers/layer-01.yml` … `layer-10.yml` |

The leaf job (`nested_leaf_happy` / `nested_leaf_sad`) is defined only in
`layer-10.yml`. Mid layers only include the next hop.

## Regenerate

From the repository root:

```bash
python tests/fixtures/shell_check/nested-10/generate.py
```

YAML under `happy/` and `sad/` is generated; edit `generate.py` and re-run
instead of hand-editing layer files.

## Smoke

```bash
poetry run gitlab-compliance shell-check \
  -p tests/fixtures/shell_check/nested-10/happy/.gitlab-ci.yml
poetry run gitlab-compliance shell-check \
  -p tests/fixtures/shell_check/nested-10/sad/.gitlab-ci.yml --failures-only
```
