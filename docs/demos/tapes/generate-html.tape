# CLI only — rendered HTML GIF is built from a browser screenshot in
# scripts/record-demos.sh (capture_html_screenshots).
Output docs/demos/gifs/generate-html-cli.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance generate -i .gitlab-ci.yml --format html -o /tmp/pipeline-docs.html && echo wrote:/tmp/pipeline-docs.html && ls -lh /tmp/pipeline-docs.html"
Enter
Sleep 5s
