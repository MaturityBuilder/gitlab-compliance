# Live: release-notes against DEMO_PROJECT.
# Requires: GITLAB_TOKEN, DEMO_PROJECT
Output docs/demos/gifs/release-notes.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type `test -n "$GITLAB_TOKEN" && test -n "$DEMO_PROJECT" || { echo "Set GITLAB_TOKEN and DEMO_PROJECT"; sleep 3; exit 1; }`
Enter
Sleep 2s
Type `gitlab-compliance release-notes --token "$GITLAB_TOKEN" --url "${DEMO_GITLAB_URL:-https://gitlab.com}" --projects "$DEMO_PROJECT" --markdown /tmp/rn-out --no-write 2>&1 | head -n 40`
Enter
Sleep 8s
