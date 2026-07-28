# Presentations

Slide decks derived from `gitlab-compliance` product documentation.

## Available decks

| File | Purpose |
| ---- | ------- |
| [gitlab-compliance-overview.pptx](gitlab-compliance-overview.pptx) | Product overview from the docs: idea, BDD model, policy pack, CLI, CI/CD, OCI, rollout |
| [gitlab-compliance-adoption.pptx](gitlab-compliance-adoption.pptx) | Adoption briefing: value, journey stages, integration patterns, success measures |

## Rebuild

```bash
python3 scripts/build_overview_pptx.py
python3 scripts/build_adoption_pptx.py
```

Requires `python-pptx` (`pip install python-pptx`).
