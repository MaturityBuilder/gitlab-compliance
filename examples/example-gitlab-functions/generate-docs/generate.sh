#!/usr/bin/env sh
set -eu

INPUT="${1:?input pipeline path required}"
FORMAT="${2:?format required}"
OUTPUT="${3:?output path required}"
OUTPUT_FILE="${4:?output_file path required}"

OUTPUT_DIR=$(dirname "${OUTPUT}")
mkdir -p "${OUTPUT_DIR}"

gitlab-compliance generate -i "${INPUT}" --format "${FORMAT}" -o "${OUTPUT}"

printf '%s\n' "{\"name\":\"output_path\",\"value\":\"${OUTPUT}\"}" >> "${OUTPUT_FILE}"
