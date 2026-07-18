# Live: --fix-supply-chain --create-mr against DEMO_PROJECT.
# Requires: GITLAB_TOKEN (PAT/project token), DEMO_PROJECT
# Optional: DEMO_GITLAB_URL
Output docs/demos/gifs/check-create-mr.gif
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
Type `cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p create-mr.gitlab-ci.yml --project "$DEMO_PROJECT" --token "$GITLAB_TOKEN" --gitlab-url "${DEMO_GITLAB_URL:-https://gitlab.com}" --fix-supply-chain --create-mr; echo exit:$?`
Enter
Sleep 10s
