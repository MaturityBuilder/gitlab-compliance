Output docs/demos/gifs/check-console.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p .gitlab-ci.yml; echo exit:$?"
Enter
Sleep 6s
