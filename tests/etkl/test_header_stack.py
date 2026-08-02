"""Loop L — header-stack selection under ruled evidence (plan 2026-08-02 Task 2).

THE LAW UNDER TEST (general; no specimen specifics appear here or in src/ or vocab/).
Given a band whose columns are the author's own ruled grid:

  * the LEAF header row is the deepest header row whose cells align 1:1 with the ruled
    columns (exactly one cell strictly inside each column) — the derivation refuses to
    run at all unless that holds;
  * every header row ABOVE it is read by MARKS THE AUTHOR MADE, never by its text (R4):
      - the row lies above a HEADER-BLOCK RULE — a horizontal rule crossing every interior
        ruled boundary inside the header region  -> FURNITURE;
      - every cell sits strictly inside a ruled column AND shares that column's leaf-label
        alignment origin                          -> CONTINUATION;
      - anything else                             -> LEVEL, today's unchanged reading.
  * the body starts at the first line after the leaf header (unchanged: header_body_split).

REVIEW ROUND 1 rewrote the first two clauses. The original reached FURNITURE by elimination
("a cell addressed to no ruled column"), which cannot separate a leaked date line from a
short merged parent — so a genuine group label got demoted or welded and an honest
escalation became a confident wrong assertion. Both non-default roles now demand positive
evidence, and LEVEL is the default. The tests below pin that: every adversarial spanner is
A/B-compared against a BASE run with the hook disabled and must come out identical.

The SHACL oracle disposes readings that do not tile or that lose text — it does NOT judge
whether a reading is right (a caption conserves text just as a label does), so it is not
relied on for correctness anywhere here.
"""
import pytest
from rdflib import RDF

from iladub.etkl.holon import TAB


def _labels(graph):
    """Every asserted column-header label text (HeaderNode -hasLabel-> LabelCell -cellText)."""
    return [str(t)
            for h in graph.subjects(RDF.type, TAB.HeaderNode)
            for lc in graph.objects(h, TAB.hasLabel)
            for t in graph.objects(lc, TAB.cellText)]


def _captions(graph):
    return [str(t) for c in graph.subjects(RDF.type, TAB.RegionCaption)
            for t in graph.objects(c, TAB.captionText)]


def _ruled_band(pdf_path):
    """The compiled band + HierRegion for a single-table ruled page (production path)."""
    from dataclasses import replace as _replace
    from iladub.etkl.geometry import (extract_words, text_lines, extract_rules,
                                      extract_chars, extract_hrules)
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.segment import segment
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.hierarchical import classify_hierarchical
    words = extract_words(pdf_path, 0)
    pr, ph = extract_rules(pdf_path, 0), extract_hrules(pdf_path, 0)
    pc = extract_chars(pdf_path, 0) if pr else []
    out = []
    for band in detect_bands(text_lines(words)):
        for sub in segment(band):
            sr = tuple(r for r in pr if r.top <= sub.bottom and r.bottom >= sub.top)
            sh = tuple(h for h in ph if sub.top <= h.y <= sub.bottom)
            out.append(_build_ruled_band(sub, sr, sh, pc) if sr
                       else (_replace(sub, hrules=sh) if sh else sub))
    band = max(out, key=lambda b: len(b.lines))
    return band, classify_hierarchical(band)


# ---------------------------------------------------------------- the law, end to end

def test_banner_and_continuations_recovered_not_escalated(tmp_path):
    """The stacked ruled header compiles instead of escalating, and the banner does NOT
    become a header level."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    pdf = str(tmp_path / "stack.pdf")
    truth = stacked_banner_ruled_pdf(pdf)
    rep = compile_tables(pdf)
    assert not any(r.verdict == "escalated" for r in rep.regions), \
        [(r.kind, r.verdict, r.reason) for r in rep.regions]
    assert rep.score >= 0.9, f"score {rep.score:.4f}"

    labels = _labels(rep.graph)
    # the leaf header populated the columns, with the wrap fragments carried onto it...
    assert "Port" in labels, labels
    assert "Total Grain Tonnes" in labels, labels
    # ...and the banner is NOT a header level anywhere.
    assert not any(truth["banner"].split("-")[0] in lb for lb in labels), labels


def test_banner_text_is_carried_not_dropped(tmp_path):
    """§7/§5: furniture text is conserved as a tab:RegionCaption, never silently dropped."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    pdf = str(tmp_path / "stack.pdf")
    stacked_banner_ruled_pdf(pdf)
    rep = compile_tables(pdf)
    caps = " ".join(_captions(rep.graph))
    assert "Monday" in caps and "August" in caps, caps


# ---------------------------------------------------------------- the law, in isolation

def test_derived_roles_are_the_law(tmp_path):
    """The role vector is DERIVED (banner / two wrap rows), not proposed."""
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.ruledroles import derive_row_roles
    pdf = str(tmp_path / "stack.pdf")
    stacked_banner_ruled_pdf(pdf)
    band, hreg = _ruled_band(pdf)
    rows = header_rows_of(band, hreg.grid, hreg.body_line)
    assert derive_row_roles(band, rows, hreg.grid) == ("furniture", "continuation", "continuation")


def test_header_block_rule_is_the_furniture_evidence(tmp_path):
    """The ONLY thing that makes a row furniture is the author's header-block rule. Same page,
    rule removed: the row falls back to `level` (review round 1 — furniture must never be
    reached by elimination)."""
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.ruledroles import derive_row_roles
    out = {}
    for flag in (True, False):
        pdf = str(tmp_path / f"stack-{flag}.pdf")
        stacked_banner_ruled_pdf(pdf, block_rule=flag)
        band, hreg = _ruled_band(pdf)
        out[flag] = derive_row_roles(band, header_rows_of(band, hreg.grid, hreg.body_line),
                                     hreg.grid)
    assert out[True] == ("furniture", "continuation", "continuation"), out
    assert out[False] == ("level", "continuation", "continuation"), out


def test_banner_without_block_rule_is_not_demoted(tmp_path):
    """With no authorial mark, the spanning top line keeps its pre-loop-L reading as a header
    node — it is NEVER silently turned into a caption."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    pdf = str(tmp_path / "nobar.pdf")
    stacked_banner_ruled_pdf(pdf, block_rule=False)
    rep = compile_tables(pdf)
    assert _captions(rep.graph) == [], _captions(rep.graph)
    labels = _labels(rep.graph)
    assert any("Monday" in lb for lb in labels), labels          # carried as a LABEL, not furniture
    assert "Total Grain Tonnes" in labels, labels                # the evidenced part still applies


@pytest.mark.parametrize("chop_mid_word", [True, False])
def test_genuine_spanner_is_never_demoted_or_welded(tmp_path, chop_mid_word):
    """REVIEW FINDING F1/F8, both cut variants. A real merged parent with no header-block rule
    and no shared alignment origin must be left exactly as the pre-loop-L path left it: never
    welded onto a leaf label, never demoted to a caption. Asserted against a BASE run of the
    same page with the loop-L hook disabled, so this is an A/B, not a snapshot."""
    from iladub.etkl import compile_tables
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.ruledroles import derive_row_roles
    from tests.etkl.fixtures import spanner_with_space_ruled_pdf
    import iladub.etkl.ruledroles as ruledroles

    pdf = str(tmp_path / f"spanner-{chop_mid_word}.pdf")
    truth = spanner_with_space_ruled_pdf(pdf, chop_mid_word=chop_mid_word)

    band, hreg = _ruled_band(pdf)
    roles = derive_row_roles(band, header_rows_of(band, hreg.grid, hreg.body_line), hreg.grid)
    assert roles is None or all(r == "level" for r in roles), roles   # no reading is claimed

    fix = compile_tables(pdf)
    real = ruledroles.resolve_ruled_header_rows
    ruledroles.resolve_ruled_header_rows = lambda *a, **k: None       # BASE
    try:
        base = compile_tables(pdf)
    finally:
        ruledroles.resolve_ruled_header_rows = real

    assert [(r.verdict, r.reason, r.cells) for r in fix.regions] == \
           [(r.verdict, r.reason, r.cells) for r in base.regions]
    assert fix.score == base.score
    assert _captions(fix.graph) == [], _captions(fix.graph)           # never demoted
    joined = " ".join(_labels(fix.graph))
    for leaf in ("Tonnes", "Port", "Ship", "Berth"):                  # never welded onto a leaf
        assert f"{truth['parent'].split()[0]} {leaf}" not in joined, joined


def test_leaf_row_not_one_to_one_refuses(tmp_path):
    """Clause 1 is a REFUSAL, not a best effort: drop one leaf label and a ruled column is left
    without one, so the whole derivation returns nothing rather than reading the stack anyway."""
    from tests.etkl.fixtures import stacked_banner_ruled_pdf
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.ruledroles import derive_row_roles
    pdf = str(tmp_path / "stack.pdf")
    stacked_banner_ruled_pdf(pdf)
    band, hreg = _ruled_band(pdf)
    rows = header_rows_of(band, hreg.grid, hreg.body_line)
    assert derive_row_roles(band, rows, hreg.grid) is not None       # intact: decides
    maimed = rows[:-1] + [rows[-1][:-1]]                             # one column loses its label
    assert derive_row_roles(band, maimed, hreg.grid) is None


def test_borderless_band_yields_no_derivation(tmp_path):
    """No ruled evidence -> no derivation (the loop only widens the RULED path); the
    borderless ambiguous merge still escalates exactly as before."""
    from iladub.etkl import compile_tables
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.ruledroles import derive_row_roles
    from tests.etkl.fixtures import offcenter_merge_report_pdf
    pdf = str(tmp_path / "offcenter.pdf")
    offcenter_merge_report_pdf(pdf)
    band, hreg = _ruled_band(pdf)
    assert not band.rules                                  # the fixture draws no rules
    assert derive_row_roles(band, header_rows_of(band, hreg.grid, hreg.body_line),
                            hreg.grid) is None
    rep = compile_tables(pdf)
    assert any(r.reason == "MERGE_AMBIGUOUS" for r in rep.regions), \
        [(r.kind, r.verdict, r.reason) for r in rep.regions]


# ---------------------------------------------------------------- regression guards

def test_flat_table_unaffected(tmp_path):
    """A plain single-header borderless table still compiles identically."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf
    pdf = str(tmp_path / "flat.pdf")
    simple_table_pdf(pdf)
    rep = compile_tables(pdf)
    assert not any(r.verdict == "escalated" for r in rep.regions)


def test_flat_RULED_table_unaffected(tmp_path):
    """A ruled table with a single (already 1:1) header row has no non-leaf row to read:
    the derivation is a no-op and the loop-G confirmed-refinement result is unchanged."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import confirmed_split_table_pdf
    pdf = str(tmp_path / "confirmed.pdf")
    truth = confirmed_split_table_pdf(pdf)
    rep = compile_tables(pdf)
    assert not any(r.verdict == "escalated" for r in rep.regions), \
        [(r.kind, r.verdict, r.reason) for r in rep.regions]
    assert sum(r.cells for r in rep.regions) == truth["data_cells"]
