#!/usr/bin/env python3
"""Build impact briefing: check, shell scan, supply chain, document."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

INK = RGBColor(0x10, 0x22, 0x30)
SEA = RGBColor(0x1A, 0x6B, 0x63)
SEA_SOFT = RGBColor(0x3C, 0xA0, 0x94)
AMBER = RGBColor(0xC4, 0x7A, 0x28)
PAPER = RGBColor(0xF5, 0xF7, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5E, 0x70, 0x7A)
BODY = RGBColor(0x2A, 0x3B, 0x46)

TOTAL = 16


def _font(run, *, size: Pt, bold: bool = False, color: RGBColor = BODY, name: str = "Calibri") -> None:
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    latin = rpr.find(qn("a:latin"))
    if latin is None:
        latin = rpr.makeelement(qn("a:latin"), {})
        rpr.insert(0, latin)
    latin.set("typeface", name)


def _rect(slide, left, top, width, height, fill: RGBColor):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    return shape


def _box(slide, left, top, width, height):
    return slide.shapes.add_textbox(left, top, width, height)


def _text(shape, text: str, *, size: Pt, bold: bool = False, color: RGBColor = BODY, align=PP_ALIGN.LEFT) -> None:
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    for run in p.runs:
        _font(run, size=size, bold=bold, color=color)


def _bullets(shape, items: list[str], *, size: Pt = Pt(16), color: RGBColor = BODY) -> None:
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.space_after = Pt(8)
        for run in p.runs:
            _font(run, size=size, color=color)


def _lines(shape, lines: list[tuple[str, RGBColor, bool, Pt]], *, mono: bool = False) -> None:
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    name = "Consolas" if mono else "Calibri"
    for i, (text, color, bold, size) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.space_after = Pt(4)
        for run in p.runs:
            _font(run, size=size, bold=bold, color=color, name=name)


def _header(slide, title: str, subtitle: str | None = None) -> None:
    _rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.25), INK)
    _rect(slide, Inches(0), Inches(1.25), SLIDE_W, Inches(0.07), SEA)
    _text(_box(slide, Inches(0.65), Inches(0.25), Inches(12), Inches(0.5)), title, size=Pt(24), bold=True, color=WHITE)
    if subtitle:
        _text(_box(slide, Inches(0.65), Inches(0.78), Inches(12), Inches(0.35)), subtitle, size=Pt(13), color=SEA_SOFT)


def _footer(slide, page: int) -> None:
    _text(
        _box(slide, Inches(0.65), Inches(7.05), Inches(9), Inches(0.28)),
        "Impact briefing  ·  Dedicated · Nexus · tech debt · ongoing standards",
        size=Pt(11),
        color=MUTED,
    )
    _text(
        _box(slide, Inches(11.2), Inches(7.05), Inches(1.5), Inches(0.28)),
        f"{page} / {TOTAL}",
        size=Pt(11),
        color=MUTED,
        align=PP_ALIGN.RIGHT,
    )


def _bg(slide) -> None:
    _rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, PAPER)


def _card(slide, left, top, width, height):
    return _rect(slide, left, top, width, height, WHITE)


def build() -> Path:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # 1 Title
    s = prs.slides.add_slide(blank)
    _rect(s, Inches(0), Inches(0), SLIDE_W, SLIDE_H, INK)
    _rect(s, Inches(0), Inches(0), Inches(0.2), SLIDE_H, SEA)
    _rect(s, Inches(0), Inches(5.85), SLIDE_W, Inches(1.65), RGBColor(0x17, 0x30, 0x3F))
    _text(
        _box(s, Inches(0.85), Inches(1.4), Inches(11.5), Inches(0.35)),
        "IMPACT BRIEFING",
        size=Pt(13),
        bold=True,
        color=SEA_SOFT,
    )
    _text(
        _box(s, Inches(0.85), Inches(1.9), Inches(11.5), Inches(1.3)),
        "Finding CI tech debt before\nGitLab Dedicated & Nexus harden",
        size=Pt(34),
        bold=True,
        color=WHITE,
    )
    _text(
        _box(s, Inches(0.85), Inches(3.5), Inches(11), Inches(1.1)),
        "Check, shell scans, supply-chain remediations, and documentation create "
        "visibility for migration — and easy-to-understand policies keep standards "
        "alive after cutover.",
        size=Pt(17),
        color=RGBColor(0xC0, 0xD0, 0xD8),
    )
    _lines(
        _box(s, Inches(0.85), Inches(6.15), Inches(11.5), Inches(1.0)),
        [
            ("gitlab-compliance", WHITE, True, Pt(16)),
            (
                "Focus: check · shell scan · supply chain · document · readable policies",
                SEA_SOFT,
                False,
                Pt(13),
            ),
        ],
    )

    # 2 Agenda / plan
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Presentation plan", "Impact first — then the four capabilities")
    _footer(s, 2)
    items = [
        "1.  Business drivers: GitLab Dedicated migration + Nexus compliance",
        "2.  What tech debt looks like in pipeline YAML today",
        "3.  Capability map: check · shell scan · supply chain · document",
        "4.  Ongoing standards via easy-to-understand Gherkin policies",
        "5.  Deep dive on each capability and the outcome it creates",
        "6.  End-to-end debt discovery → remediate → prove → maintain",
        "7.  Recommended rollout for migration programmes",
    ]
    _bullets(_box(s, Inches(0.9), Inches(1.75), Inches(11.5), Inches(4.8)), items, size=Pt(19))

    # 3 Business drivers
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Why this matters now", "Two demands that expose hidden pipeline debt")
    _footer(s, 3)
    _card(s, Inches(0.65), Inches(1.65), Inches(5.9), Inches(4.7))
    _rect(s, Inches(0.65), Inches(1.65), Inches(5.9), Inches(0.65), SEA)
    _text(_box(s, Inches(0.9), Inches(1.78), Inches(5.4), Inches(0.4)), "GitLab Dedicated migration", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(0.95), Inches(2.55), Inches(5.3), Inches(3.5)),
        [
            "Need a clear inventory of CI configuration risk before cutover",
            "Floating tags and unpinned includes break predictability on new runners/registries",
            "Migration windows favour known debt over surprise failures",
            "Stakeholders need readable evidence of readiness — not YAML archaeology",
        ],
        size=Pt(14),
    )
    _card(s, Inches(6.8), Inches(1.65), Inches(5.9), Inches(4.7))
    _rect(s, Inches(6.8), Inches(1.65), Inches(5.9), Inches(0.65), AMBER)
    _text(_box(s, Inches(7.05), Inches(1.78), Inches(5.4), Inches(0.4)), "Nexus compliance demand", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(7.1), Inches(2.55), Inches(5.3), Inches(3.5)),
        [
            "Approved artefact sources and immutable pins become mandatory",
            ":latest and unversioned includes conflict with Nexus controls",
            "Digest pinning and release-lag policies prove control effectiveness",
            "Auto-fix MRs shorten the gap between finding and closing debt",
        ],
        size=Pt(14),
    )

    # 4 Tech debt catalogue
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Tech debt we need to find", "Typical CI debt that blocks migration and compliance")
    _footer(s, 4)
    debts = [
        ("Mutable images", ":latest / untagged images — non-reproducible builds"),
        ("Unpinned includes", "project/component refs on main or floating tags"),
        ("Stale supply chain", "Includes / images lagging beyond agreed windows"),
        ("Weak execution guards", "Jobs missing rules: — accidental production runs"),
        ("Template bypass", "Jobs not extending org-standard CI templates"),
        ("Undocumented pipelines", "No living reference for Dedicated cutover reviews"),
        ("API setting gaps", "Unmasked variables / risky project settings"),
        ("Policy drift", "Standards only in wikis — not enforced in MR gates"),
    ]
    for i, (h, body) in enumerate(debts):
        col = i % 4
        row = i // 4
        left = Inches(0.5 + col * 3.2)
        top = Inches(1.6 + row * 2.45)
        _card(s, left, top, Inches(3.05), Inches(2.2))
        _rect(s, left, top, Inches(3.05), Inches(0.1), SEA if row == 0 else AMBER)
        _text(_box(s, left + Inches(0.2), top + Inches(0.3), Inches(2.65), Inches(0.55)), h, size=Pt(14), bold=True, color=INK)
        _text(_box(s, left + Inches(0.2), top + Inches(0.95), Inches(2.65), Inches(1.0)), body, size=Pt(12), color=BODY)

    # 5 Capability map
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Capability map", "Find debt now — keep standards clear afterwards")
    _footer(s, 5)
    caps = [
        ("check", "Fail or report when Gherkin policies are violated", "Find debt with evidence (file:line)"),
        ("Shell scan", "Run the same check from a laptop/CI shell across repos", "Inventory debt before Dedicated cutover"),
        ("Supply chain", "--fix-supply-chain / --fix-policies / --create-mr", "Close Nexus-related pin & version debt"),
        ("document", "generate + document gitstrings", "Expose pipeline shape for migration reviews"),
        ("Policies", "Readable Gherkin scenarios shared by security and delivery", "Maintain ongoing standards without wiki drift"),
    ]
    for i, (title, how, impact) in enumerate(caps):
        top = Inches(1.5 + i * 0.98)
        _card(s, Inches(0.65), top, Inches(12), Inches(0.9))
        _rect(s, Inches(0.65), top, Inches(2.4), Inches(0.9), SEA)
        _text(
            _box(s, Inches(0.75), top + Inches(0.25), Inches(2.2), Inches(0.4)),
            title,
            size=Pt(14),
            bold=True,
            color=WHITE,
            align=PP_ALIGN.CENTER,
        )
        _text(_box(s, Inches(3.3), top + Inches(0.12), Inches(9), Inches(0.3)), how, size=Pt(13), color=BODY)
        _text(
            _box(s, Inches(3.3), top + Inches(0.48), Inches(9), Inches(0.3)),
            f"Impact: {impact}",
            size=Pt(12),
            bold=True,
            color=SEA,
        )

    # 6 Ongoing standards via readable policies
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(
        s,
        "Ongoing standards — written so people understand them",
        "Gherkin policies stay the living contract after migration",
    )
    _footer(s, 6)
    _text(
        _box(s, Inches(0.7), Inches(1.5), Inches(12), Inches(0.45)),
        "Migration finds debt once. Readable policies keep the same rules enforceable every merge.",
        size=Pt(15),
        color=BODY,
    )
    _card(s, Inches(0.65), Inches(2.1), Inches(6.0), Inches(4.3))
    _text(_box(s, Inches(0.95), Inches(2.3), Inches(5.4), Inches(0.4)), "Why easy-to-understand policies matter", size=Pt(15), bold=True, color=INK)
    _bullets(
        _box(s, Inches(0.95), Inches(2.9), Inches(5.4), Inches(3.2)),
        [
            "Security and delivery share one language — not buried YAML lore",
            "New Nexus / Dedicated rules are written as scenarios, not slides",
            "Policy packs version in a repo or OCI registry — segregation of duty",
            "Metadata IDs and titles make audit findings explainable",
            "Standards survive staff change because the contract is in CI",
        ],
        size=Pt(13),
    )
    _card(s, Inches(6.9), Inches(2.1), Inches(5.8), Inches(4.3))
    _rect(s, Inches(6.9), Inches(2.1), Inches(5.8), Inches(0.08), SEA)
    _lines(
        _box(s, Inches(7.15), Inches(2.35), Inches(5.3), Inches(3.8)),
        [
            ("# Anyone can read the standard", MUTED, False, Pt(12)),
            ("Scenario: Job images must not use latest", INK, True, Pt(13)),
            ("  Given I have any job defined", SEA, True, Pt(13)),
            ("  When it has image", SEA, True, Pt(13)),
            ('  Then its image must not match ":latest$"', SEA, True, Pt(13)),
            ("", MUTED, False, Pt(8)),
            ("# METADATA keeps ownership clear", MUTED, False, Pt(12)),
            ("# title: Disallow latest image tags", MUTED, False, Pt(12)),
            ("# custom.id: GLCI-IMAGE-PINNING-001", MUTED, False, Pt(12)),
            ("# custom.severity: HIGH", MUTED, False, Pt(12)),
        ],
        mono=True,
    )

    # 7 check deep dive
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "check — find debt with proof", "gitlab-compliance check -f policies/ -p .gitlab-ci.yml")
    _footer(s, 7)
    _bullets(
        _box(s, Inches(0.8), Inches(1.6), Inches(11.5), Inches(2.2)),
        [
            "Runs readable Gherkin policies against pipeline YAML (and optional GitLab API settings)",
            "Reports violations with path:line so teams can act without guessing",
            "Output formats that fit migration programmes: console, markdown, HTML, MR comment, Code Quality",
            "Warn-only first (allow_failure), then enforce — same readable policies, stronger gate",
        ],
        size=Pt(15),
    )
    _card(s, Inches(0.65), Inches(4.0), Inches(12), Inches(2.4))
    _text(_box(s, Inches(0.95), Inches(4.2), Inches(11.4), Inches(0.35)), "Migration / Nexus / ongoing impact", size=Pt(15), bold=True, color=INK)
    _bullets(
        _box(s, Inches(0.95), Inches(4.65), Inches(11.4), Inches(1.5)),
        [
            "Creates a repeatable readiness scorecard per project before Dedicated move",
            "Makes Nexus pin/version expectations testable — not a spreadsheet exercise",
            "The same easy-to-read policies keep standards enforced after cutover",
        ],
        size=Pt(14),
    )

    # 7 shell scan
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Shell scan — inventory before you migrate", "Local CLI sweeps across repositories (same engine as CI)")
    _footer(s, 8)
    _text(
        _box(s, Inches(0.7), Inches(1.55), Inches(12), Inches(0.5)),
        "There is no separate “shellcheck” product mode — impact comes from running check in the shell to discover debt at scale.",
        size=Pt(14),
        color=BODY,
    )
    _card(s, Inches(0.65), Inches(2.2), Inches(12), Inches(2.0))
    _lines(
        _box(s, Inches(0.95), Inches(2.4), Inches(11.4), Inches(1.6)),
        [
            ("# Example: scan a clone for supply-chain and pin debt", MUTED, False, Pt(13)),
            ("pip install gitlab-compliance", BODY, False, Pt(14)),
            ("gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \\", SEA, True, Pt(14)),
            ("  --format markdown -o COMPLIANCE-REPORT.md", SEA, True, Pt(14)),
            ("# Optional: --with-builtin · --project · --strict for API hardening", MUTED, False, Pt(13)),
        ],
        mono=True,
    )
    _bullets(
        _box(s, Inches(0.8), Inches(4.5), Inches(11.5), Inches(2.0)),
        [
            "Platform teams can batch-scan migration cohorts and rank projects by debt severity",
            "Produces artefacts for Dedicated cutover boards and Nexus exception reviews",
            "Same policies later become CI gates — no double standard between discovery and enforcement",
        ],
        size=Pt(15),
    )

    # 8 supply chain
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Supply chain — close the debt Nexus cares about", "--fix-supply-chain · --fix-policies · --create-mr")
    _footer(s, 9)
    left = [
        "Detect floating tags, unpinned includes, release lag, digest gaps",
        "Age windows (e.g. 30-day adoption, 90-day lag) for pragmatic upgrades",
        "Pin job/service images to @sha256 digests",
        "Bump outdated project/component include refs to latest semver",
    ]
    right = [
        "--fix-supply-chain rewrites before policies re-run",
        "--fix-policies remediates allowlisted failed scenarios only",
        "--create-mr opens a reviewable supply-chain fix MR",
        "Scheduled CI job can keep debt from re-accumulating",
    ]
    _card(s, Inches(0.65), Inches(1.6), Inches(5.9), Inches(4.7))
    _text(_box(s, Inches(0.95), Inches(1.85), Inches(5.3), Inches(0.4)), "What it finds / fixes", size=Pt(16), bold=True, color=INK)
    _bullets(_box(s, Inches(0.95), Inches(2.45), Inches(5.3), Inches(3.5)), left, size=Pt(14))
    _card(s, Inches(6.8), Inches(1.6), Inches(5.9), Inches(4.7))
    _text(_box(s, Inches(7.1), Inches(1.85), Inches(5.3), Inches(0.4)), "How it supports programmes", size=Pt(16), bold=True, color=INK)
    _bullets(_box(s, Inches(7.1), Inches(2.45), Inches(5.3), Inches(3.5)), right, size=Pt(14))

    # 9 document
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "document / generate — make debt discussable", "Living pipeline docs for migration and compliance forums")
    _footer(s, 10)
    _card(s, Inches(0.65), Inches(1.6), Inches(5.9), Inches(4.7))
    _rect(s, Inches(0.65), Inches(1.6), Inches(5.9), Inches(0.6), SEA)
    _text(_box(s, Inches(0.9), Inches(1.72), Inches(5.4), Inches(0.4)), "generate", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(0.95), Inches(2.45), Inches(5.3), Inches(3.5)),
        [
            "Full pipeline reference from .gitlab-ci.yml",
            "Formats: markdown, swagger-markdown, HTML",
            "Exclude/group to match audience",
            "Attach as CI artefact for Dedicated review packs",
        ],
        size=Pt(14),
    )
    _card(s, Inches(6.8), Inches(1.6), Inches(5.9), Inches(4.7))
    _rect(s, Inches(6.8), Inches(1.6), Inches(5.9), Inches(0.6), AMBER)
    _text(_box(s, Inches(7.05), Inches(1.72), Inches(5.4), Inches(0.4)), "document gitstrings", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(7.1), Inches(2.45), Inches(5.3), Inches(3.5)),
        [
            "Fragment docs for inputs, variables, snippets",
            "Decorators in YAML or markdown fences",
            "Keeps READMEs honest without rewriting by hand",
            "Helps Nexus/security reviewers see intent quickly",
        ],
        size=Pt(14),
    )

    # 10 Dedicated support
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Supporting the GitLab Dedicated migration", "From unknown debt → sequenced remediation → cutover confidence")
    _footer(s, 11)
    steps = [
        ("Discover", "Shell-scan migration cohorts with check; export markdown/HTML debt reports."),
        ("Prioritise", "Rank projects by supply-chain severity, API gaps, and undocumented pipelines."),
        ("Remediate", "Use --fix-supply-chain / --fix-policies / --create-mr; review diffs before merge."),
        ("Document", "generate + gitstrings artefacts for Dedicated readiness packs."),
        ("Maintain", "Readable Gherkin policies + CI gates keep standards ongoing after cutover."),
    ]
    for i, (title, body) in enumerate(steps):
        top = Inches(1.55 + i * 0.95)
        _card(s, Inches(0.65), top, Inches(12), Inches(0.85))
        _rect(s, Inches(0.65), top, Inches(2.2), Inches(0.85), SEA)
        _text(_box(s, Inches(0.75), top + Inches(0.25), Inches(2.0), Inches(0.4)), title, size=Pt(14), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _text(_box(s, Inches(3.1), top + Inches(0.25), Inches(9.2), Inches(0.45)), body, size=Pt(14), color=BODY)

    # 11 Nexus support
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Supporting Nexus compliance demand", "Prove control: pin, version, lag windows, and remediation trail")
    _footer(s, 12)
    rows = [
        ("Nexus expectation", "gitlab-compliance response"),
        ("Only approved / known artefact sources", "Image + include pinning policies; digest preferred"),
        ("No mutable latest tags", "Gherkin rules fail :latest; auto-pin to sha256"),
        ("Versions within agreed freshness", "Release-lag / latest-N / adoption-window scenarios"),
        ("Evidence for audits", "Markdown/HTML/Code Quality reports + policy metadata IDs"),
        ("Sustainable standards", "Readable Gherkin policies + scheduled supply-chain fix MRs"),
    ]
    for i, (left, right) in enumerate(rows):
        top = Inches(1.5 + i * 0.8)
        bg = SEA if i == 0 else WHITE
        lc = WHITE if i == 0 else INK
        rc = WHITE if i == 0 else BODY
        _rect(s, Inches(0.65), top, Inches(5.7), Inches(0.7), bg)
        _rect(s, Inches(6.45), top, Inches(6.2), Inches(0.7), bg)
        _text(_box(s, Inches(0.85), top + Inches(0.18), Inches(5.3), Inches(0.4)), left, size=Pt(13), bold=(i == 0), color=lc)
        _text(_box(s, Inches(6.65), top + Inches(0.18), Inches(5.8), Inches(0.4)), right, size=Pt(13), bold=(i == 0), color=rc)

    # 12 end-to-end flow
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "End-to-end: discover → fix → prove → maintain", "One toolchain across migration, compliance, and ongoing standards")
    _footer(s, 13)
    flow = [
        ("1. Shell check", "Scan repos; write COMPLIANCE-REPORT.md"),
        ("2. Triage debt", "Group by pin / lag / rules / docs gaps"),
        ("3. Auto-remediate", "--fix-supply-chain [--fix-policies]"),
        ("4. Human review", "--create-mr → approve digest/version bumps"),
        ("5. Document", "generate / document gitstrings for evidence"),
        ("6. Maintain", "Readable policies + CI gates keep standards ongoing"),
    ]
    for i, (h, body) in enumerate(flow):
        col = i % 3
        row = i // 3
        left = Inches(0.55 + col * 4.2)
        top = Inches(1.7 + row * 2.4)
        _card(s, left, top, Inches(4.0), Inches(2.15))
        _rect(s, left, top, Inches(4.0), Inches(0.1), SEA)
        _text(_box(s, left + Inches(0.25), top + Inches(0.35), Inches(3.5), Inches(0.45)), h, size=Pt(15), bold=True, color=INK)
        _text(_box(s, left + Inches(0.25), top + Inches(0.95), Inches(3.5), Inches(0.9)), body, size=Pt(13), color=BODY)

    # 13 commands cheat sheet
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Command cheat sheet", "Copy-ready starting points from product docs")
    _footer(s, 14)
    cmds = [
        ("Find debt", "gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md"),
        ("Strict API", "gitlab-compliance check -f policies/ -p .gitlab-ci.yml --project \"$CI_PROJECT_PATH\" --strict"),
        ("Supply chain fix", "gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix-supply-chain --create-mr --project \"$CI_PROJECT_PATH\""),
        ("Pipeline docs", "gitlab-compliance generate -i .gitlab-ci.yml --format html -o pipeline-reference/index.html"),
        ("Fragment docs", "gitlab-compliance document gitstrings -i .gitlab-ci.yml -o README.md"),
    ]
    for i, (label, cmd) in enumerate(cmds):
        top = Inches(1.5 + i * 0.95)
        _card(s, Inches(0.55), top, Inches(12.2), Inches(0.85))
        _rect(s, Inches(0.55), top, Inches(2.4), Inches(0.85), SEA)
        _text(_box(s, Inches(0.65), top + Inches(0.25), Inches(2.2), Inches(0.4)), label, size=Pt(13), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _text(_box(s, Inches(3.15), top + Inches(0.2), Inches(9.3), Inches(0.5)), cmd, size=Pt(11), color=BODY)

    # 14 measures
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Impact measures", "How programme leads know debt is under control — and stays that way")
    _footer(s, 15)
    measures = [
        ("% projects scanned", "Migration cohort coverage via shell/CI check"),
        ("Open critical findings", "Unpinned / latest / lag beyond policy"),
        ("Time to remediate", "Finding → merged supply-chain MR"),
        ("Docs freshness", "generate artefacts attached to readiness packs"),
        ("Policy clarity", "Teams can explain failed scenarios without YAML experts"),
        ("Standards stickiness", "Readable policies enforced after Dedicated cutover"),
    ]
    for i, (h, body) in enumerate(measures):
        col = i % 3
        row = i // 3
        left = Inches(0.55 + col * 4.2)
        top = Inches(1.7 + row * 2.4)
        _card(s, left, top, Inches(4.0), Inches(2.15))
        _text(_box(s, left + Inches(0.25), top + Inches(0.35), Inches(3.5), Inches(0.55)), h, size=Pt(15), bold=True, color=SEA)
        _text(_box(s, left + Inches(0.25), top + Inches(1.0), Inches(3.5), Inches(0.85)), body, size=Pt(13), color=BODY)

    # 15 next steps
    s = prs.slides.add_slide(blank)
    _rect(s, Inches(0), Inches(0), SLIDE_W, SLIDE_H, INK)
    _rect(s, Inches(0), Inches(0), Inches(0.2), SLIDE_H, SEA)
    _text(_box(s, Inches(0.85), Inches(1.2), Inches(11.5), Inches(0.7)), "Recommended next steps", size=Pt(32), bold=True, color=WHITE)
    actions = [
        "Pick the Dedicated migration cohort and run a shell check sweep this week",
        "Baseline against the security policy pack (image / include / lag)",
        "Open supply-chain fix MRs for the highest-severity projects",
        "Publish generate/HTML docs into migration readiness packs",
        "Author Nexus-aligned rules as readable Gherkin — then move CI from warn-only to blocking",
    ]
    box = _box(s, Inches(0.85), Inches(2.15), Inches(11.5), Inches(3.5))
    tf = box.text_frame
    tf.clear()
    for i, item in enumerate(actions):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{i + 1}.  {item}"
        p.space_after = Pt(12)
        for run in p.runs:
            _font(run, size=Pt(16), color=WHITE)
    _text(
        _box(s, Inches(0.85), Inches(6.2), Inches(11.5), Inches(0.5)),
        "Docs: maturitybuilder.github.io/gitlab-compliance  ·  pip install gitlab-compliance",
        size=Pt(13),
        color=SEA_SOFT,
    )

    out = Path("/workspace/docs/presentations/gitlab-compliance-dedicated-nexus-impact.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    print(f"Wrote {build()}")
