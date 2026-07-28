#!/usr/bin/env python3
"""Build a non-technical secure-by-design stakeholder briefing."""

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

TOTAL = 12


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
        p.space_after = Pt(9)
        for run in p.runs:
            _font(run, size=size, color=color)


def _lines(shape, lines: list[tuple[str, RGBColor, bool, Pt]]) -> None:
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, (text, color, bold, size) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.space_after = Pt(5)
        for run in p.runs:
            _font(run, size=size, bold=bold, color=color)


def _header(slide, title: str, subtitle: str | None = None) -> None:
    _rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.25), INK)
    _rect(slide, Inches(0), Inches(1.25), SLIDE_W, Inches(0.07), SEA)
    _text(_box(slide, Inches(0.65), Inches(0.25), Inches(12), Inches(0.5)), title, size=Pt(24), bold=True, color=WHITE)
    if subtitle:
        _text(_box(slide, Inches(0.65), Inches(0.78), Inches(12), Inches(0.35)), subtitle, size=Pt(13), color=SEA_SOFT)


def _footer(slide, page: int) -> None:
    _text(
        _box(slide, Inches(0.65), Inches(7.05), Inches(9), Inches(0.28)),
        "Gitlab Compliance  ·  Secure by design",
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


def _notes(slide, text: str) -> None:
    """Attach presenter notes for the slide."""
    notes = slide.notes_slide
    tf = notes.notes_text_frame
    tf.clear()
    tf.word_wrap = True
    # Split on blank lines into paragraphs for readability in PowerPoint.
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = para
        p.space_after = Pt(8)
        for run in p.runs:
            _font(run, size=Pt(12), color=BODY)


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
        _box(s, Inches(0.85), Inches(1.5), Inches(11.5), Inches(0.35)),
        "SECURE BY DESIGN",
        size=Pt(13),
        bold=True,
        color=SEA_SOFT,
    )
    _text(
        _box(s, Inches(0.85), Inches(2.0), Inches(11.5), Inches(1.2)),
        "Gitlab Compliance",
        size=Pt(42),
        bold=True,
        color=WHITE,
    )
    _text(
        _box(s, Inches(0.85), Inches(3.35), Inches(11), Inches(1.3)),
        "Measure control coverage, detect non-conforming configuration, and place controls "
        "in delivery pipelines — so Dedicated migration and Nexus expectations are guided by evidence.",
        size=Pt(18),
        color=RGBColor(0xC0, 0xD0, 0xD8),
    )
    _lines(
        _box(s, Inches(0.85), Inches(6.2), Inches(11.5), Inches(0.9)),
        [
            ("Measurement · Detection of non-conforming code · Place controls", WHITE, True, Pt(15)),
            ("Non-conformance is usually unintentional drift — not deliberate rule-breaking", SEA_SOFT, False, Pt(13)),
        ],
    )
    _notes(
        s,
        "Open by framing secure by design — not a blame conversation.\n\n"
        "Key message: Gitlab Compliance helps us measure control coverage, detect "
        "non-conforming configuration, and place controls so Dedicated and Nexus work "
        "is guided by evidence.\n\n"
        "Emphasise that non-conformance is usually unintentional drift — people are not "
        "trying to break rules. We need visibility and detection so we can place the "
        "right controls early.",
    )

    # 2 Agenda
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "What we will cover", "Secure by design — measured and detectable")
    _footer(s, 2)
    _bullets(
        _box(s, Inches(0.9), Inches(1.8), Inches(11.5), Inches(4.8)),
        [
            "1.  Why delivery needs measurable controls",
            "2.  Dedicated migration and Nexus as design moments",
            "3.  What Gitlab Compliance enables",
            "4.  Where controls are identified and placed",
            "5.  Readable policies that keep standards ongoing",
            "6.  What good looks like — identify and place controls",
        ],
        size=Pt(20),
    )
    _notes(
        s,
        "Walk the agenda briefly. Promise outcomes, not tooling detail.\n\n"
        "Signal the destination early: what good looks like is identifying and placing "
        "controls — with continuous measurement and detection afterwards.",
    )

    # 3 Opportunity / design gap (not blame)
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(
        s,
        "The design gap",
        "Without measurement, unintentional non-conformance stays invisible until late",
    )
    _footer(s, 3)
    cards = [
        ("Hard to measure", "We cannot see which delivery setups meet the intended control standard."),
        (
            "Hard to detect",
            "Non-conforming configuration often appears late — near go-live — when change is expensive.",
        ),
        (
            "Hard to place controls",
            "Expectations exist in guidance, but drift into non-conformance is usually unintentional — not deliberate.",
        ),
        ("Hard to decide with data", "Progress relies on anecdotes instead of a shared, evidence-based view."),
    ]
    for i, (h, body) in enumerate(cards):
        col = i % 2
        row = i // 2
        left = Inches(0.65 + col * 6.3)
        top = Inches(1.7 + row * 2.4)
        _card(s, left, top, Inches(6.0), Inches(2.15))
        _rect(s, left, top, Inches(0.12), Inches(2.15), AMBER if i % 2 else SEA)
        _text(_box(s, left + Inches(0.4), top + Inches(0.35), Inches(5.3), Inches(0.45)), h, size=Pt(18), bold=True, color=INK)
        _text(_box(s, left + Inches(0.4), top + Inches(0.95), Inches(5.3), Inches(0.9)), body, size=Pt(15), color=BODY)
    _notes(
        s,
        "Stay non-judgemental. The problem is missing measurement and late detection — "
        "not people ignoring standards.\n\n"
        "Say explicitly: drift into non-conformance is usually unintentional. Without "
        "detection, we only discover it when change is expensive.\n\n"
        "Transition: Dedicated and Nexus make this design gap visible and urgent.",
    )

    # 4 Why now
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Why this matters now", "Two moments to design security into delivery — not bolt it on later")
    _footer(s, 4)
    _card(s, Inches(0.65), Inches(1.65), Inches(5.9), Inches(4.7))
    _rect(s, Inches(0.65), Inches(1.65), Inches(5.9), Inches(0.7), SEA)
    _text(_box(s, Inches(0.9), Inches(1.8), Inches(5.4), Inches(0.45)), "GitLab Dedicated migration", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(0.95), Inches(2.6), Inches(5.3), Inches(3.4)),
        [
            "Cutover is a chance to baseline control coverage",
            "Undetected non-conformance becomes schedule and service risk",
            "Readiness should be evidenced, not assumed",
            "Secure by design means controls are identified and placed before the move",
        ],
        size=Pt(15),
    )
    _card(s, Inches(6.8), Inches(1.65), Inches(5.9), Inches(4.7))
    _rect(s, Inches(6.8), Inches(1.65), Inches(5.9), Inches(0.7), AMBER)
    _text(_box(s, Inches(7.05), Inches(1.8), Inches(5.4), Inches(0.45)), "Nexus compliance demand", size=Pt(17), bold=True, color=WHITE)
    _bullets(
        _box(s, Inches(7.1), Inches(2.6), Inches(5.3), Inches(3.4)),
        [
            "Trusted, approved components need detectable controls",
            "Freshness and pinning expectations must be measurable",
            "Evidence of control effectiveness supports assurance",
            "Remediation stays reviewable and sustainable",
        ],
        size=Pt(15),
    )
    _notes(
        s,
        "Position Dedicated and Nexus as design moments — chances to build security in, "
        "not bolt it on after cutover.\n\n"
        "Left: migration needs a measured baseline of controls before we move.\n\n"
        "Right: Nexus needs detectable pinning and freshness controls, with evidence that "
        "those controls work.\n\n"
        "Avoid ‘people must follow rules’ language — focus on placing measurable controls.",
    )

    # 5 What it enables
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(
        s,
        "What Gitlab Compliance enables",
        "Measurement and detection of non-conforming code — then place controls",
    )
    _footer(s, 5)
    _text(
        _box(s, Inches(0.7), Inches(1.55), Inches(12), Inches(0.55)),
        "It turns agreed security expectations into measurable signals — detecting unintentional "
        "non-conforming configuration early so controls can be placed with confidence.",
        size=Pt(16),
        color=BODY,
    )
    points = [
        ("Measure", "See where intended controls are present or missing across projects."),
        (
            "Detect non-conformance",
            "Find non-conforming code and configuration before approval — usually drift, not intent.",
        ),
        ("Guide behaviour", "Shared evidence supports consistent, data-driven decisions."),
        ("Place controls", "Readable policies define the control; checks confirm it is in place."),
        ("Strengthen supply chain", "Pinning and freshness controls align with Nexus expectations."),
        ("Keep visibility", "Living summaries make pipeline intent understandable over time."),
    ]
    for i, (h, body) in enumerate(points):
        col = i % 3
        row = i // 3
        left = Inches(0.55 + col * 4.2)
        top = Inches(2.3 + row * 2.2)
        _card(s, left, top, Inches(4.0), Inches(2.0))
        _rect(s, left, top, Inches(4.0), Inches(0.1), SEA)
        _text(_box(s, left + Inches(0.25), top + Inches(0.3), Inches(3.5), Inches(0.45)), h, size=Pt(15), bold=True, color=INK)
        _text(_box(s, left + Inches(0.25), top + Inches(0.9), Inches(3.5), Inches(0.85)), body, size=Pt(13), color=BODY)
    _notes(
        s,
        "This is the capability story in business language.\n\n"
        "Stress the sequence: measure → detect non-conforming code → place controls → "
        "guide behaviour with shared evidence.\n\n"
        "Remind the room that detected non-conformance is usually drift, not intent. "
        "The tool creates early signals so we can act calmly.",
    )

    # 6 How capabilities map
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "How the tool supports secure by design", "Four capabilities that make controls measurable")
    _footer(s, 6)
    caps = [
        (
            "Check",
            "Detect non-conforming configuration against the intended control standard.",
        ),
        ("Scan widely", "Measure coverage across the migration cohort with a shared evidence view."),
        ("Supply-chain controls", "Place pinning and freshness controls that support Nexus expectations."),
        ("Document", "Keep a clear record of pipeline design so control intent stays visible."),
    ]
    for i, (h, body) in enumerate(caps):
        top = Inches(1.55 + i * 1.2)
        _card(s, Inches(0.65), top, Inches(12), Inches(1.08))
        _rect(s, Inches(0.65), top, Inches(2.8), Inches(1.08), SEA)
        _text(
            _box(s, Inches(0.75), top + Inches(0.32), Inches(2.6), Inches(0.45)),
            h,
            size=Pt(14),
            bold=True,
            color=WHITE,
            align=PP_ALIGN.CENTER,
        )
        _text(_box(s, Inches(3.7), top + Inches(0.3), Inches(8.6), Inches(0.55)), body, size=Pt(15), color=BODY)
    _notes(
        s,
        "Map each capability to a secure-by-design outcome without diving into commands.\n\n"
        "Check = detect non-conformance. Scan = measure cohort coverage. Supply-chain = "
        "place Nexus-aligned controls. Document = keep control intent visible.\n\n"
        "If asked for detail: these work from pipeline configuration and optional project "
        "settings — still keep the conversation on outcomes.",
    )

    # 7 Control areas
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Where we identify and place controls", "Control areas that make delivery safer by design")
    _footer(s, 7)
    debts = [
        ("Trusted components", "Control: only known, pinned building blocks."),
        ("Dependency freshness", "Control: stay within agreed update windows."),
        ("Release guards", "Control: steps run only when intended."),
        ("Shared delivery patterns", "Control: standard templates are applied consistently."),
        ("Pipeline visibility", "Control: current design is documented and reviewable."),
        ("Automated assurance", "Control: expectations are checked continuously, not only on paper."),
    ]
    for i, (h, body) in enumerate(debts):
        col = i % 3
        row = i // 3
        left = Inches(0.55 + col * 4.2)
        top = Inches(1.65 + row * 2.4)
        _card(s, left, top, Inches(4.0), Inches(2.15))
        _text(_box(s, left + Inches(0.25), top + Inches(0.35), Inches(3.5), Inches(0.55)), h, size=Pt(15), bold=True, color=SEA)
        _text(_box(s, left + Inches(0.25), top + Inches(1.0), Inches(3.5), Inches(0.85)), body, size=Pt(13), color=BODY)
    _notes(
        s,
        "Use this as a control catalogue — where we identify and place protections.\n\n"
        "For each card, say ‘this is a control we can define, detect against, and place’.\n\n"
        "Tie trusted components and freshness to Nexus; tie release guards and patterns to "
        "predictable Dedicated cutover. Automated assurance means the control is checked "
        "continuously, not only written in guidance.",
    )

    # 8 Journey
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "From non-conformance to control", "A practical path to secure-by-design delivery")
    _footer(s, 8)
    steps = [
        ("1", "Identify", "Baseline where intended controls are missing or incomplete."),
        (
            "2",
            "Prioritise",
            "Focus first on highest-impact non-conformance for Dedicated and Nexus.",
        ),
        ("3", "Place controls", "Apply readable policies and remediations with reviewable change."),
        ("4", "Measure", "Track coverage and non-conformance findings with shared reports."),
        (
            "5",
            "Sustain",
            "Keep detection in place so unintentional drift is caught after go-live.",
        ),
    ]
    for i, (num, title, body) in enumerate(steps):
        top = Inches(1.55 + i * 0.95)
        _card(s, Inches(0.65), top, Inches(12), Inches(0.85))
        _rect(s, Inches(0.8), top + Inches(0.15), Inches(0.7), Inches(0.55), SEA)
        _text(
            _box(s, Inches(0.8), top + Inches(0.25), Inches(0.7), Inches(0.4)),
            num,
            size=Pt(16),
            bold=True,
            color=WHITE,
            align=PP_ALIGN.CENTER,
        )
        _text(_box(s, Inches(1.8), top + Inches(0.12), Inches(3.2), Inches(0.35)), title, size=Pt(16), bold=True, color=INK)
        _text(_box(s, Inches(5.1), top + Inches(0.2), Inches(7.2), Inches(0.5)), body, size=Pt(14), color=BODY)
    _notes(
        s,
        "Walk the five steps as the programme path.\n\n"
        "Identify → Prioritise → Place controls → Measure → Sustain.\n\n"
        "Pause on ‘Place controls’ — that is the heart of what good looks like. Sustain "
        "matters so unintentional drift is still detected after Dedicated go-live.",
    )

    # 9 Readable policies
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "Controls written so people understand them", "Readable policies make secure by design sustainable")
    _footer(s, 9)
    _text(
        _box(s, Inches(0.7), Inches(1.5), Inches(12), Inches(0.5)),
        "A control only works if people can understand it, place it, and detect when configuration drifts.",
        size=Pt(15),
        color=BODY,
    )
    _card(s, Inches(0.65), Inches(2.15), Inches(5.9), Inches(4.2))
    _text(_box(s, Inches(0.95), Inches(2.4), Inches(5.3), Inches(0.4)), "Why readable controls matter", size=Pt(16), bold=True, color=INK)
    _bullets(
        _box(s, Inches(0.95), Inches(3.0), Inches(5.3), Inches(3.0)),
        [
            "Security and delivery share one understandable control definition",
            "New Nexus or Dedicated expectations can be expressed clearly",
            "Non-conformance findings are explainable without specialist decoding",
            "Control ownership is visible and versioned",
            "Standards remain usable as teams and suppliers change",
        ],
        size=Pt(14),
    )
    _card(s, Inches(6.8), Inches(2.15), Inches(5.9), Inches(4.2))
    _text(_box(s, Inches(7.1), Inches(2.4), Inches(5.3), Inches(0.4)), "Example of a clear control", size=Pt(16), bold=True, color=INK)
    _text(
        _box(s, Inches(7.1), Inches(3.1), Inches(5.3), Inches(2.8)),
        "“Software images used in delivery must not rely on an open-ended ‘latest’ version.”\n\n"
        "That control is written in plain language, checked automatically, and creates a measurable "
        "signal when non-conforming configuration appears — usually by accident, not intent.",
        size=Pt(14),
        color=BODY,
    )
    _notes(
        s,
        "Readable policies are how controls stay understandable after migration.\n\n"
        "Read the example aloud. Then note: when the check fires, it usually means "
        "unintentional drift — a measurable signal that a control is not yet in place.\n\n"
        "This is how security and delivery share one control definition without needing "
        "specialist decoding in every forum.",
    )

    # 10 Programme support
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "How this supports our programmes", "Evidence-led readiness for Dedicated and Nexus")
    _footer(s, 10)
    rows = [
        ("Programme need", "Secure-by-design response"),
        ("Know control coverage before Dedicated cutover", "Measured baseline across the migration cohort"),
        ("Meet Nexus expectations", "Detectable pinning and freshness controls"),
        (
            "Reduce late surprise",
            "Non-conforming code detected early enough to place controls calmly",
        ),
        ("Decide with data", "Shared reports replace assumption-based status"),
        ("Keep controls after the move", "Readable policies remain the ongoing design contract"),
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
    _notes(
        s,
        "Use the table as a programme translation layer: need → secure-by-design response.\n\n"
        "Highlight early detection of non-conforming code so controls can be placed calmly — "
        "not in a rush at go-live.\n\n"
        "Close the slide on continuity: readable policies remain the design contract after "
        "the Dedicated move.",
    )

    # 11 What good looks like
    s = prs.slides.add_slide(blank)
    _bg(s)
    _header(s, "What good looks like", "Identifying and placing controls — then measuring continuously")
    _footer(s, 11)
    measures = [
        ("Controls identified", "Intended controls are defined in plain language for each risk area."),
        ("Controls placed", "Those controls are applied in delivery pipelines, not only described."),
        (
            "Non-conformance detected",
            "Non-conforming code is spotted automatically before approval.",
        ),
        ("Measurement shared", "Coverage and findings are visible in a common evidence view."),
        (
            "Data-driven improvement",
            "Priorities follow measured non-conformance severity, not anecdote.",
        ),
        ("Secure by design sustained", "The same controls remain detectable after Dedicated cutover."),
    ]
    for i, (h, body) in enumerate(measures):
        col = i % 3
        row = i // 3
        left = Inches(0.55 + col * 4.2)
        top = Inches(1.65 + row * 2.4)
        _card(s, left, top, Inches(4.0), Inches(2.15))
        _text(_box(s, left + Inches(0.25), top + Inches(0.35), Inches(3.5), Inches(0.5)), h, size=Pt(15), bold=True, color=SEA)
        _text(_box(s, left + Inches(0.25), top + Inches(0.95), Inches(3.5), Inches(0.95)), body, size=Pt(13), color=BODY)
    _notes(
        s,
        "This is the success definition. Lead with identify and place controls.\n\n"
        "Then: non-conformance is detected automatically; measurement is shared; priorities "
        "follow data; the same controls stay detectable after cutover.\n\n"
        "Do not turn this into a people-performance story. It is a control-design story.",
    )

    # 12 Closing — secure by design outcome
    s = prs.slides.add_slide(blank)
    _rect(s, Inches(0), Inches(0), SLIDE_W, SLIDE_H, INK)
    _rect(s, Inches(0), Inches(0), Inches(0.2), SLIDE_H, SEA)
    _text(_box(s, Inches(0.85), Inches(1.2), Inches(11.5), Inches(0.7)), "Secure by design in practice", size=Pt(30), bold=True, color=WHITE)
    actions = [
        "Identify the controls that matter for Dedicated readiness and Nexus assurance",
        "Measure where those controls are already in place across the cohort",
        "Detect unintentional non-conforming code early and place controls with reviewable change",
        "Use shared evidence to prioritise and track improvement",
        "Keep readable policies as the ongoing design standard after go-live",
    ]
    box = _box(s, Inches(0.85), Inches(2.15), Inches(11.5), Inches(3.6))
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
        "What good looks like: controls identified and placed — with continuous detection of non-conformance.",
        size=Pt(14),
        color=SEA_SOFT,
    )
    _notes(
        s,
        "Close on secure by design in practice — five practical steps, not a leadership ask.\n\n"
        "Repeat the punchline: what good looks like is controls identified and placed, with "
        "continuous detection of non-conformance.\n\n"
        "Invite discussion on which control areas to baseline first for the Dedicated cohort "
        "and Nexus expectations.",
    )

    out = Path("/workspace/docs/presentations/gitlab-compliance-stakeholder-briefing.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    print(f"Wrote {build()}")
