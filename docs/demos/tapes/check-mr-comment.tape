# Live: posts a compliance report comment to an existing MR.
# Requires: GITLAB_TOKEN, DEMO_PROJECT, DEMO_MR_IID (or CI_MERGE_REQUEST_IID)
# Optional: DEMO_GITLAB_URL
Output docs/demos/gifs/check-post-mr-comment.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type `test -n "$GITLAB_TOKEN" && test -n "$DEMO_PROJECT" && test -n "${DEMO_MR_IID:-$CI_MERGE_REQUEST_IID}" || { echo "Set GITLAB_TOKEN DEMO_PROJECT DEMO_MR_IID"; sleep 3; exit 1; }`
Enter
Sleep 2s
Type `cd docs/demos/fixtures && gitlab-compliance check -f policies/ -p .gitlab-ci.yml --project "$DEMO_PROJECT" --token "$GITLAB_TOKEN" --gitlab-url "${DEMO_GITLAB_URL:-https://gitlab.com}" --format mr-comment --post-mr-comment --mr-iid "${DEMO_MR_IID:-$CI_MERGE_REQUEST_IID}"; echo exit:$?`
Enter
Sleep 8s
