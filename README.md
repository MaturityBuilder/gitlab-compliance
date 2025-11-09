# Gitlab Docs

## 📖 Overview
GitLab Docs is your portable, Python-powered sidekick for keeping GitLab CI/CD pipelines well-documented.
If your system supports Python 3, you can install it instantly — no complex setup, no platform restrictions.

### 💡 Why it matters:

Code documentation is crucial.

Pipeline documentation is critical.

As pipelines grow, the what, when, and where of your workflows often get lost.

That’s where GitLab Docs comes in — a simple, elegant CLI tool that automatically generates and updates Markdown documentation for your pipelines, right alongside your code.

### ✨ Key Features
🛠 Portable — Works anywhere Python 3 runs.

📜 Markdown Output — Friendly for developers, perfect for GitLab README integration.

🔄 Auto-Update Mode — Insert or refresh documentation between customizable markers.

🧩 Multi-Block Support — Maintain different sections for different workflows.

🧪 Dry Run Mode — Preview changes without touching files.

### Python

```bash
pip3 install --user gitlab-docs
```

### Docker

```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```
or

```bash
podman run -it -v $(PWD):/gitlab-docs charlieasmith93/gitlab-docs
```