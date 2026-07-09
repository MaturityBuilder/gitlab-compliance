#!/usr/bin/env bash
# Export MaturityBuilder Project 3 and gitlab-compliance issues for roadmap sync.
# Requires: gh CLI authenticated as a user with project + issues read access.
set -euo pipefail

OWNER="${OWNER:-MaturityBuilder}"
REPO="${REPO:-MaturityBuilder/gitlab-compliance}"
PROJECT_NUMBER="${PROJECT_NUMBER:-3}"
OUT_DIR="${OUT_DIR:-./roadmap-export}"

mkdir -p "$OUT_DIR"

echo "Exporting project ${OWNER} #${PROJECT_NUMBER}..."
gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --format json \
  > "${OUT_DIR}/project-${PROJECT_NUMBER}-items.json"

echo "Exporting issues for ${REPO}..."
gh issue list -R "$REPO" --state all --limit 200 \
  --json number,title,state,labels,url,body,milestone,assignees \
  > "${OUT_DIR}/issues.json"

echo "Wrote ${OUT_DIR}/project-${PROJECT_NUMBER}-items.json and ${OUT_DIR}/issues.json"
