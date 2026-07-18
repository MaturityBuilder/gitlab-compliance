# Live: policies push/pull against an OCI registry.
# Requires: DEMO_OCI_REF (e.g. registry.example.com/org/demo-policies:demo)
Output docs/demos/gifs/policies-push-pull.gif
Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set TypingSpeed 40ms
Set PlaybackSpeed 0.5
Set Theme "Catppuccin Mocha"

Type `test -n "$DEMO_OCI_REF" || { echo "Set DEMO_OCI_REF"; sleep 3; exit 1; }`
Enter
Sleep 2s
Type `cd docs/demos/fixtures && gitlab-compliance policies push -f policies/ "$DEMO_OCI_REF" && gitlab-compliance policies pull "oci://$DEMO_OCI_REF" -o /tmp/pulled-policies && ls /tmp/pulled-policies`
Enter
Sleep 10s
