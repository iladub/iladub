"""R155 — a boundary the author drew THROUGH one marked-content item does not divide that row.

Spec: docs/superpowers/specs/2026-09-01-the-author-drew-one-label-design.md

R154 gave `_row_dividers` the predicate *a boundary divides a row only where the ink on both sides
CLEARS it*. That distinguishes "cuts ink" from "falls in a gap". It provably cannot distinguish a
WORD GAP from a COLUMN GUTTER, and the spec §3.1-§3.3 measures three constant-free geometric
candidates and refutes all three — the last one generally: on WHO's own header, intra-word KERNING
gaps (0.042-0.064pt) and the inter-word gap (2.758pt) differ only in MAGNITUDE, so any predicate
separating them is a tuned constant (CLAUDE.md §8).

The fact that separates them is not geometric. It is the marked-content id the author's own
producer wrote into the page: WHO's 'Z-scores (weight in kg)' is ONE mcid spanning the boundary,
and the twelve column labels on the line below are TWELVE. Measured corpus-wide, the rule declines
8 of 3613 boundaries, and four of the seven documents carry NO marked content at all, so they are
byte-identical BY CONSTRUCTION rather than by a threshold that happens to spare them.

Evidence-positive and open-world: a boundary is declined only where an enclosing run is PRESENT,
never inferred from absence (CLAUDE.md §8).
"""
from iladub.etkl.geometry import Char, rule_aware_lines


def _run(text: str, x0: float, mcid, width: float = 4.0, top: float = 10.0) -> list[Char]:
    """One abutting glyph box per character, all carrying the same marked-content id — the layout
    a renderer produces for a single text-showing run inside one marked-content item.

    A ' ' in `text` becomes a real SPACE GLYPH, because that is what the renderer emits: WHO's
    header carries space glyphs at x=(591.756, 594.501), 2.745pt wide, sitting in the 2.758pt gap.
    `_cell_text` joins two non-space glyphs with a space only when a space glyph lies between them
    — a presence test with no magnitude — so a fixture without one does not model the real page."""
    return [Char(ch, x0 + i * width, x0 + (i + 1) * width, top, top + 8.0, mcid=mcid)
            for i, ch in enumerate(text)]


def test_a_boundary_inside_one_marked_content_run_does_not_divide_it():
    """THE R155 CASE. Two words of one label, separated by a real gap wide enough that R154's
    clearance predicate honours the boundary between them — but the author marked both as one
    item, so the label is one cell."""
    label = _run("in", 100.0, mcid=7, width=8.0) + _run(" ", 116.0, mcid=7, width=8.0) \
        + _run("kg)", 124.0, mcid=7, width=8.0)          # gap 116..124, boundary 120 inside it
    lines = rule_aware_lines(label, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["in kg)"]


def test_the_same_geometry_with_two_mcids_still_divides():
    """The discriminator is the mcid and NOTHING else. Identical boxes, identical gap, identical
    boundary — two marked-content items, so two cells. This is WHO line 1's column gutter, and it
    is why the rule cannot be restated as a gap-width rule."""
    two = _run("in", 100.0, mcid=7, width=8.0) + _run(" ", 116.0, mcid=7, width=8.0) \
        + _run("kg)", 124.0, mcid=8, width=8.0)
    lines = rule_aware_lines(two, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["in", "kg)"]


def test_absent_marked_content_is_inert():
    """The open-world half, and the load-bearing one: with no mcid the rule has no evidence and
    must not fire. Same geometry as the first test; `mcid=None` is `Char`'s default, so this is
    also the guarantee that every untagged document is byte-identical."""
    untagged = _run("in", 100.0, mcid=None, width=8.0) + _run(" ", 116.0, mcid=None, width=8.0) \
        + _run("kg)", 124.0, mcid=None, width=8.0)
    lines = rule_aware_lines(untagged, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["in", "kg)"]


def test_a_boundary_between_runs_of_the_same_mcid_in_different_rows_is_untouched():
    """mcid is a PAGE-scoped id, not a row-scoped one, and the runs are built per row from that
    row's ink. A second row reusing the same id must not inherit the first row's span."""
    row0 = _run("in", 100.0, mcid=7, width=8.0) + _run(" ", 116.0, mcid=7, width=8.0) \
        + _run("kg)", 124.0, mcid=7, width=8.0)
    row1 = _run("ab", 100.0, mcid=7, width=8.0, top=40.0) \
        + _run(" ", 116.0, mcid=7, width=8.0, top=40.0) \
        + _run("cd", 124.0, mcid=9, width=8.0, top=40.0)
    lines = rule_aware_lines(row0 + row1, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["in kg)"]
    assert [w.text for w in lines[1].words] == ["ab", "cd"]


def test_the_r154_clearance_predicate_still_governs_within_one_mcid():
    """R155 only ever DECLINES boundaries. It must not resurrect one R154 declined: a boundary
    cutting through ink stays declined whether or not marked content encloses it."""
    cut = _run("Zscores", 100.0, mcid=7)                  # ink spans 100.0 .. 128.0
    lines = rule_aware_lines(cut, [90.0, 110.0, 118.0, 140.0])
    assert [w.text for w in lines[0].words] == ["Zscores"]
