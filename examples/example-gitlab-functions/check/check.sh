#!/usr/bin/env sh
set -eu

POLICIES="${1:?policies path required}"
PIPELINE="${2:?pipeline path required}"

gitlab-compliance check -f "${POLICIES}" -p "${PIPELINE}"
