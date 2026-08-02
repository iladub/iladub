"""Loop L — header-stack selection under ruled evidence (plan 2026-08-02 Task 2).

THE LAW UNDER TEST (general; no specimen specifics appear here or in src/ or vocab/).
Given a band whose columns are the author's own ruled grid:

  * the LEAF header row is the deepest header row whose cells align 1:1 with the ruled
    columns (exactly one cell strictly inside each column) — the derivation refuses to
    run at all unless that holds;
  * every header row ABOVE it is read by its ink's relation to those columns, never by
    its text (R4's lesson):
      - the row's ink covers EVERY ruled column, or one of its cells claims no column at
        all (inside none, covering none)  -> FURNITURE, a banner drawn over the grid;
      - some cell covers a whole ruled column                -> LEVEL, a group label
        (today's unchanged parent pipeline);
      - otherwise every cell is strictly inside one column   -> CONTINUATION, a wrap
        fragment of that column's leaf label;
  * the body starts at the first line after the leaf header (unchanged: header_body_split).

The reading is DISPOSED by the same SHACL tiling + conservation oracle loop C uses, so a
derivation that does not tile changes nothing.
"""
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
