#!/usr/bin/env bash
# Install VHS and ttyd for CI (demos-offline job) with supply-chain checks.
#
# - VHS: release tarball SHA256 must match the pinned digest (GitHub release metadata).
# - ttyd: built from source at a pinned commit (no unsigned release binary).
set -euo pipefail

VHS_VERSION="0.11.0"
VHS_TARBALL="vhs_${VHS_VERSION}_Linux_x86_64.tar.gz"
VHS_URL="https://github.com/charmbracelet/vhs/releases/download/v${VHS_VERSION}/${VHS_TARBALL}"
# From charmbracelet/vhs release v0.11.0 asset digest (GitHub API).
VHS_TARBALL_SHA256="99cb634587eaae0473c1ea377db80c3a048c27f99fe0a7febb1a1e8cb7ee5009"

TTYD_TAG="1.7.7"
TTYD_COMMIT="40e79c706be14029b391f369bee6613c31667abb"
TTYD_REPO="https://github.com/tsl0922/ttyd.git"

verify_sha256() {
  local file="$1"
  local expected="$2"
  local label="$3"
  local actual
  actual="$(sha256sum "${file}" | awk '{print $1}')"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "error: ${label} SHA256 mismatch" >&2
    echo "  expected: ${expected}" >&2
    echo "  actual:   ${actual}" >&2
    exit 1
  fi
}

install_vhs() {
  local dest="/tmp/${VHS_TARBALL}"
  curl -fsSL "${VHS_URL}" -o "${dest}"
  verify_sha256 "${dest}" "${VHS_TARBALL_SHA256}" "${VHS_TARBALL}"
  tar -xzf "${dest}" -C /tmp
  sudo install -m 755 "/tmp/vhs_${VHS_VERSION}_Linux_x86_64/vhs" /usr/local/bin/vhs
}

install_ttyd_from_source() {
  local src_dir
  src_dir="$(mktemp -d)"
  git clone --depth 1 --branch "${TTYD_TAG}" "${TTYD_REPO}" "${src_dir}"
  local head
  head="$(git -C "${src_dir}" rev-parse HEAD)"
  if [[ "${head}" != "${TTYD_COMMIT}" ]]; then
    echo "error: ttyd tag ${TTYD_TAG} points to ${head}, expected ${TTYD_COMMIT}" >&2
    exit 1
  fi
  cmake -S "${src_dir}" -B "${src_dir}/build" -DCMAKE_BUILD_TYPE=Release
  cmake --build "${src_dir}/build" -j"$(nproc)"
  sudo install -m 755 "${src_dir}/build/ttyd" /usr/local/bin/ttyd
}

install_vhs
install_ttyd_from_source

vhs --version
ttyd --version
