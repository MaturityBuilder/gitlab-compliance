# CLI only — rendered HTML GIF is built from a browser screenshot in
# scripts/record-demos.sh (capture_html_screenshots).
Output docs/demos/gifs/check-html-cli.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p .gitlab-ci.yml --format html -o /tmp/compliance-report.html && echo wrote:/tmp/compliance-report.html && ls -lh /tmp/compliance-report.html"
Enter
Sleep 5s
