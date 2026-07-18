Output docs/demos/gifs/generate-markdown.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance generate -i .gitlab-ci.yml --format markdown -o /tmp/pipeline-docs.md && head -n 45 /tmp/pipeline-docs.md"
Enter
Sleep 5s
