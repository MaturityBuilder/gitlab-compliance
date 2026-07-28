# Offline preview of the --create-mr flow (no GitLab API).
# Live recording: check-create-mr.tape via bash scripts/record-demos.sh live
Output docs/demos/gifs/check-create-mr.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type "cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p create-mr.gitlab-ci.yml --dry-run"
Enter
Sleep 6s
Type "echo 'Live MR create: add --fix --create-mr --project ... --token ...'"
Enter
Sleep 4s
Type "echo 'Re-record with: bash scripts/record-demos.sh live'"
Enter
Sleep 4s
