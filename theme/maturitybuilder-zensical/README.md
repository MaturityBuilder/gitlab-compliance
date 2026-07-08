# MaturityBuilder theme for Zensical

Shared documentation theme for [MaturityBuilder](https://github.com/MaturityBuilder) projects. It targets Zensical’s **modern** variant with custom light/dark palettes, typography, and polish that stays consistent across product sites.

## Install

From a MaturityBuilder repository that vendors this package:

```bash
pip install "zensical>=0.0.47" "./theme/maturitybuilder-zensical"
```

Or pin the theme from Git (adjust path if the theme lives in another repo):

```bash
pip install "zensical>=0.0.47" "maturitybuilder-zensical-theme @ git+https://github.com/MaturityBuilder/gitlab-compliance.git@main#subdirectory=theme/maturitybuilder-zensical"
```

With Poetry:

```toml
[tool.poetry.group.docs.dependencies]
zensical = "^0.0.47"
maturitybuilder-zensical-theme = { path = "theme/maturitybuilder-zensical", develop = true }
```

## Site configuration

Minimal `mkdocs.yml` (or equivalent `zensical.toml`):

```yaml
theme:
  name: maturitybuilder
  variant: modern
  logo: assets/logo.svg
  font:
    text: Plus Jakarta Sans
    code: JetBrains Mono
  palette:
    - scheme: maturitybuilder
      primary: custom
      accent: custom
      toggle:
        icon: lucide/moon
        name: Switch to dark mode
    - scheme: maturitybuilder-dark
      primary: custom
      accent: custom
      toggle:
        icon: lucide/sun
        name: Switch to light mode
```

Add a project logo under your `docs_dir` (for example `docs/assets/logo.svg`). The bundled theme logo is only a fallback reference; each site should ship its own asset.

## Develop

```bash
pip install -e "./theme/maturitybuilder-zensical"
zensical serve
```

## License

MIT
