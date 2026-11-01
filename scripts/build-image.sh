#!/usr/bin/env bash
# Build the Wolfi image with melange + apko.
#
# Pins to update when refreshing the toolchain (Dependabot does not cover these):
#   MELANGE_IMAGE / APKO_IMAGE digests below
#   image/apko.lock.json (regenerated after melange build)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

MELANGE_IMAGE="${MELANGE_IMAGE:-cgr.dev/chainguard/melange:latest@sha256:c6eea71bf274b94d84c04238861d7abea55b61b50da921b88c194c112123593b}"
APKO_IMAGE="${APKO_IMAGE:-cgr.dev/chainguard/apko:latest@sha256:c53d15d53090012cdc9f138b667a73a283b0b5bba1b61963ae84be6e28cfe5a0}"

IMAGE_REF="${IMAGE_REF:-maturitybuilder/gitlab-compliance:local}"
ARCH="${ARCH:-x86_64}"
# apko tags single-arch images as <ref>-amd64 / <ref>-arm64
case "${ARCH}" in
  x86_64|amd64) APKO_ARCH_TAG="amd64" ;;
  aarch64|arm64) APKO_ARCH_TAG="arm64" ;;
  *) APKO_ARCH_TAG="${ARCH}" ;;
esac
OUT_TAR="${OUT_TAR:-${ROOT}/gitlab-compliance-image.tar}"
SIGNING_KEY="${SIGNING_KEY:-${ROOT}/melange.rsa}"
PACKAGE_VERSION="${PACKAGE_VERSION:-}"
LOAD_IMAGE="${LOAD_IMAGE:-0}"

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
fi

if [[ -z "${PACKAGE_VERSION}" ]]; then
  if command -v poetry >/dev/null 2>&1; then
    PACKAGE_VERSION="$(poetry version -s)"
  else
    PACKAGE_VERSION="$(
      python3 - <<'PY'
import re
from pathlib import Path
text = Path("pyproject.toml").read_text()
match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
if not match:
    raise SystemExit("unable to parse version from pyproject.toml")
print(match.group(1))
PY
    )"
  fi
fi

echo "Building gitlab-compliance ${PACKAGE_VERSION} for ${ARCH} -> ${IMAGE_REF}"

rm -rf "${ROOT}/packages"
mkdir -p "${ROOT}/packages"

VARS_FILE="${ROOT}/image/.melange-vars.yaml"
cat > "${VARS_FILE}" <<EOF
version: "${PACKAGE_VERSION}"
EOF

if [[ ! -f "${SIGNING_KEY}" ]]; then
  echo "Generating temporary melange signing key at ${SIGNING_KEY}"
  "${DOCKER[@]}" run --rm \
    -v "${ROOT}:/work" \
    -w /work \
    --entrypoint melange \
    "${MELANGE_IMAGE}" \
    keygen
fi

# Prefer bubblewrap: nested docker.sock mounts cannot see melange's host-side
# workspace paths. On GitHub-hosted runners bubblewrap works with --privileged.
"${DOCKER[@]}" run --rm --privileged \
  -v "${ROOT}:/work" \
  -w /work \
  --entrypoint melange \
  "${MELANGE_IMAGE}" \
  build image/melange.yaml \
  --arch "${ARCH}" \
  --source-dir /work \
  --out-dir /work/packages \
  --signing-key "/work/$(basename "${SIGNING_KEY}")" \
  --runner bubblewrap \
  --vars-file /work/image/.melange-vars.yaml

# Refresh the lockfile so the local APK checksum matches this build; Wolfi
# package pins stay reproducible across rebuilds of the same index.
"${DOCKER[@]}" run --rm \
  -v "${ROOT}:/work" \
  -w /work \
  --entrypoint apko \
  "${APKO_IMAGE}" \
  lock image/apko.yaml \
  --arch "${ARCH}" \
  --keyring-append /work/melange.rsa.pub \
  --output /work/image/apko.lock.json

"${DOCKER[@]}" run --rm \
  -v "${ROOT}:/work" \
  -w /work \
  --entrypoint apko \
  "${APKO_IMAGE}" \
  build image/apko.yaml \
  "${IMAGE_REF}" \
  "/work/$(basename "${OUT_TAR}")" \
  --arch "${ARCH}" \
  --keyring-append /work/melange.rsa.pub \
  --lockfile /work/image/apko.lock.json

# Containers often create root-owned artifacts; make them writable for the runner.
if command -v sudo >/dev/null 2>&1; then
  sudo chown -R "$(id -u):$(id -g)" \
    "${ROOT}/packages" \
    "${ROOT}/image/apko.lock.json" \
    "${OUT_TAR}" \
    "${ROOT}/melange.rsa" \
    "${ROOT}/melange.rsa.pub" \
    "${VARS_FILE}" 2>/dev/null || true
fi

echo "Wrote ${OUT_TAR}"

if [[ "${LOAD_IMAGE}" == "1" ]]; then
  "${DOCKER[@]}" load -i "${OUT_TAR}"
  ARCH_REF="${IMAGE_REF}-${APKO_ARCH_TAG}"
  if "${DOCKER[@]}" image inspect "${ARCH_REF}" >/dev/null 2>&1; then
    "${DOCKER[@]}" tag "${ARCH_REF}" "${IMAGE_REF}"
    echo "Tagged ${ARCH_REF} as ${IMAGE_REF}"
  fi
  echo "Loaded ${IMAGE_REF}"
else
  echo "Load with: docker load -i ${OUT_TAR}"
fi

# Ephemeral melange keys must not remain in the workspace: Trivy fs scans
# (and similar secret scanners) treat melange.rsa as a HIGH private-key finding.
rm -f "${ROOT}/melange.rsa" "${ROOT}/melange.rsa.pub" "${VARS_FILE}"
