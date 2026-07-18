"""Supply-chain pins for CI demo tool installation."""

import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install-ci-demo-tools.sh"


def test_vhs_tarball_sha256_is_pinned() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    match = re.search(r'VHS_TARBALL_SHA256="([a-f0-9]{64})"', text)
    assert match, "expected pinned VHS tarball SHA256 in install-ci-demo-tools.sh"
    assert match.group(1) == (
        "99cb634587eaae0473c1ea377db80c3a048c27f99fe0a7febb1a1e8cb7ee5009"
    )


def test_ttyd_commit_is_pinned() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    match = re.search(r'TTYD_COMMIT="([a-f0-9]{40})"', text)
    assert match, "expected pinned ttyd commit in install-ci-demo-tools.sh"
    assert match.group(1) == "40e79c706be14029b391f369bee6613c31667abb"
