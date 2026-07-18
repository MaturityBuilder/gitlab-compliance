Output docs/demos/gifs/check-markdown.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p .gitlab-ci.yml --format markdown -o /tmp/compliance-report.md; echo '--- report ---'; head -n 40 /tmp/compliance-report.md"
Enter
Sleep 6s
