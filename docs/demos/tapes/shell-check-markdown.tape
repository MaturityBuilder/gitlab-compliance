Output docs/demos/gifs/shell-check-markdown.gif
Set FontSize 14
Set Width 1200
Set Height 700
Set TypingSpeed 15ms
Set PlaybackSpeed 0.8

Hide
Type "clear"
Enter
Show

Type "poetry run gitlab-compliance shell-check -p docs/demos/fixtures/shell-check/bad.gitlab-ci.yml --format markdown -o /tmp/shell-check-report.md && head -n 40 /tmp/shell-check-report.md"
Enter
Sleep 5s
