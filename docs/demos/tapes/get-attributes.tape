Output docs/demos/gifs/get-attributes.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance get-attributes -i .gitlab-ci.yml -a image,stage -o /tmp/attrs.md && cat /tmp/attrs.md"
Enter
Sleep 5s
