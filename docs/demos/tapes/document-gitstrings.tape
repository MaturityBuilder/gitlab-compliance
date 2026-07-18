Output docs/demos/gifs/document-gitstrings.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cp docs/demos/fixtures/gitstrings.md /tmp/gitstrings-demo.md && gitlab-compliance document gitstrings -i /tmp/gitstrings-demo.md -o /tmp/gitstrings-demo.md && sed -n '1,60p' /tmp/gitstrings-demo.md"
Enter
Sleep 5s
