"""The accounting currency-marker column (spec 2026-08-05-unit-marker-column-design.md).

A borderless column whose every non-blank cell is the SAME currency symbol is a unit
marker on its numeric right neighbor, not a column of the table. Recognition is the
unit-marker-column.rq AXIOM over a DEDICATED typed-cell evidence graph (marker-local
tab:CurrencyGlyph typing — the shared celltype lattice is deliberately untouched so
every existing query stays byte-identical). Measured driver: apple p0, where `$`
columns fabricate ncols=9 for a 5-column statement."""
from iladub.etkl.unitmarker import derive_marker_columns

# The apple accounting shape: label col 0, `$` marker col 1 (first + total rows only),
# numeric value col 2.
APPLE_SHAPE = [
    (0, 0, "Net sales:"),
    (1, 0, "Products"), (1, 1, "$"), (1, 2, "78,678"),
    (2, 0, "Services"),              (2, 2, "30,739"),
    (3, 0, "Total net sales"), (3, 1, "$"), (3, 2, "109,417"),
]


def test_same_symbol_column_with_numeric_neighbor_is_derived():
    assert derive_marker_columns(APPLE_SHAPE, 3) == ((1, "$"),)


def test_footnote_star_column_is_refused():
    # `*` is not a currency symbol — the column stays an ordinary column.
    cells = [(r, c, t if t != "$" else "*") for (r, c, t) in APPLE_SHAPE]
    assert derive_marker_columns(cells, 3) == ()


def test_mixed_symbols_are_refused():
    # $ and € in one column: not the SAME symbol -> no absorption.
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "10"), (2, 1, "€"), (2, 2, "20")]
    assert derive_marker_columns(cells, 3) == ()


def test_symbol_column_without_numeric_neighbor_is_refused():
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "abc"), (2, 1, "$"), (2, 2, "def")]
    assert derive_marker_columns(cells, 3) == ()


def test_year_header_neighbor_is_refused():
    # I1 (final-review): the neighbor condition is SAME-ROW. Column 1's glyphs sit on
    # rows 1-2, but the ONLY numeric cell in column 2 is the row-0 YEAR HEADER ("2026")
    # over an all-TEXT body ("Sales"/"Revenue") — no row has a glyph in c AND a
    # Numeric/Currency cell in c+1 on the SAME row, so absorption must be refused. Pre-
    # fix (ANY-row neighbor), this column wrongly derived as a marker.
    cells = [
        (0, 0, "x"), (0, 2, "2026"),
        (1, 1, "$"), (1, 2, "Sales"),
        (2, 1, "$"), (2, 2, "Revenue"),
    ]
    assert derive_marker_columns(cells, 3) == ()


def test_column_with_any_non_symbol_cell_is_refused():
    # One stray text cell among the symbols disqualifies the whole column.
    cells = APPLE_SHAPE + [(2, 1, "note")]
    assert derive_marker_columns(cells, 3) == ()


def test_blank_cells_do_not_disqualify():
    # Blanks are wildcards, exactly as in the split query's Blank convention.
    cells = APPLE_SHAPE + [(2, 1, "-")]
    assert derive_marker_columns(cells, 3) == ((1, "$"),)


def test_two_marker_columns_both_derive():
    cells = [
        (0, 0, "A"), (0, 1, "$"), (0, 2, "10"), (0, 3, "$"), (0, 4, "20"),
        (1, 0, "B"), (1, 1, "$"), (1, 2, "11"), (1, 3, "$"), (1, 4, "21"),
    ]
    assert derive_marker_columns(cells, 5) == ((1, "$"), (3, "$"))


# ---------------------------------------------------------------- absorption

def _mkband(rows, cols):
    """A synthetic borderless Band: rows = list of {col_index: text}, cols = left x
    per column (Courier-ish 40pt-wide words at exact x positions)."""
    from iladub.etkl.geometry import Word, Line
    from iladub.etkl.bands import Band
    lines = []
    for r, row in enumerate(rows):
        top = 100.0 + r * 14.0
        words = tuple(Word(text=t, x0=cols[c], x1=cols[c] + max(8.0, 6.0 * len(t)),
                           top=top, bottom=top + 10.0)
                      for c, t in sorted(row.items()))
        lines.append(Line(words=words, top=top, bottom=top + 10.0))
    return Band(tuple(lines), lines[0].top, lines[-1].bottom)


APPLE_BAND_ROWS = [
    {0: "Label", 2: "Amount", 4: "Total"},
    {0: "Products", 1: "$", 2: "78,678", 3: "$", 4: "272,629"},
    {0: "Services", 2: "30,739", 4: "91,728"},
    {0: "Other", 2: "11,729", 4: "34,035"},
    {0: "Sum", 1: "$", 2: "121,146", 3: "$", 4: "398,392"},
]
APPLE_BAND_COLS = {0: 72.0, 1: 220.0, 2: 260.0, 3: 380.0, 4: 420.0}


def test_absorb_removes_marker_words_and_carries_them():
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = _mkband(APPLE_BAND_ROWS, APPLE_BAND_COLS)
    out = absorb_unit_markers(band)
    texts = [w.text for ln in out.lines for w in ln.words]
    assert "$" not in texts                       # the glyphs left the word stream
    assert len(out.unit_markers) == 2             # one per absorbed column
    syms = sorted(m[0] for m in out.unit_markers)
    assert syms == ["$", "$"]
    # provenance: each marker carries one region per absorbed glyph (2 rows drew $)
    assert all(len(m[2]) == 2 for m in out.unit_markers)
    # neighbor_x falls inside the value column's x-range
    assert any(260.0 <= m[1] <= 380.0 for m in out.unit_markers)


def test_absorb_is_identity_without_markers():
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = _mkband([{0: "A", 1: "10"}, {0: "B", 1: "20"}, {0: "C", 1: "30"}],
                   {0: 72.0, 1: 200.0})
    out = absorb_unit_markers(band)
    assert out.unit_markers == ()
    assert [w.text for ln in out.lines for w in ln.words] == \
           [w.text for ln in band.lines for w in ln.words]


def test_absorb_is_identity_for_ruled_bands():
    from dataclasses import replace
    from iladub.etkl.geometry import Rule
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = replace(_mkband(APPLE_BAND_ROWS, APPLE_BAND_COLS),
                   rules=(Rule(x=250.0, top=100.0, bottom=170.0),))
    assert absorb_unit_markers(band) is band


# ---------------------------------------------------------------- emission + membrane

def test_marker_facts_emitted_with_provenance(tmp_path):
    from rdflib import Namespace, RDF
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import currency_marker_column_pdf
    TAB = Namespace("https://w3id.org/iladub/tab#")
    pdf = str(tmp_path / "marker.pdf")
    currency_marker_column_pdf(pdf)
    rep = compile_tables(pdf, page_number=0)
    assert any(r.verdict == "asserted" for r in rep.regions), \
        [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    markers = list(rep.graph.subjects(RDF.type, TAB.UnitMarker))
    assert markers, "no tab:UnitMarker emitted"
    for m in markers:
        assert list(rep.graph.objects(m, TAB.markerSymbol))
        assert list(rep.graph.objects(m, TAB.markerRegion)), "marker without provenance"
        assert not list(rep.graph.objects(m, TAB.hasBBox)), \
            "R19 trap: marker must never carry tab:hasBBox"
        cols = list(rep.graph.subjects(TAB.hasUnitMarker, m))
        assert len(cols) == 1, "marker must hang off exactly one column"


def test_unit_marker_shape_negative():
    # The membrane refuses a marker without provenance (the example pair's negative half).
    from pyshacl import validate
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    m = URIRef("urn:um:bad")
    g.add((m, RDF.type, TAB.UnitMarker))
    g.add((m, TAB.markerSymbol, Literal("$")))          # no markerRegion
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, _ = validate(g, shacl_graph=shapes, advanced=True)
    assert not conforms


def test_example_pair_conforms():
    from pyshacl import validate
    from rdflib import Graph
    g = Graph().parse("examples/tables/unit-marker.ttl", format="turtle")
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, report = validate(g, shacl_graph=shapes, advanced=True)
    assert conforms, report


def test_transposed_marker_attaches_to_table_not_a_column():
    """Fix round 1 (CRITICAL): assert_transposed_region keys its `{table_uri}-c{k}`
    leaf-column URIs by PHYSICAL ROW index (the axis flip — logical column k <- physical
    row k), while column_of(neighbor_x, boundaries) resolves a PHYSICAL COLUMN index — a
    different axis entirely. Reusing that index would attach the marker to a
    coincidentally-numbered, semantically unrelated LeafColumn. compile.py's transposed
    call site passes boundaries=None for exactly this reason; this test exercises
    _emit_unit_markers directly with boundaries=None and checks the marker hangs off the
    TABLE, carries its symbol + provenance, and mints NO `-c{n}` column subject."""
    from dataclasses import replace
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    from iladub.etkl.compile import _emit_unit_markers
    TAB = Namespace("https://w3id.org/iladub/tab#")
    band = replace(_mkband(APPLE_BAND_ROWS, APPLE_BAND_COLS),
                   unit_markers=(("$", 300.0, ((220.0, 100.0, 228.0, 110.0),)),))
    g = Graph()
    table_uri = URIRef("urn:test:ttable0")
    _emit_unit_markers(g, table_uri, band, None)

    markers = list(g.subjects(RDF.type, TAB.UnitMarker))
    assert len(markers) == 1
    m = markers[0]
    assert list(g.objects(m, TAB.markerSymbol)) == [Literal("$")]
    assert list(g.objects(m, TAB.markerRegion)), "marker without provenance"

    holders = list(g.subjects(TAB.hasUnitMarker, m))
    assert holders == [table_uri], "marker must hang off the table, not a column"
    assert not any(str(h).startswith(f"{table_uri}-c") for h in holders), \
        "no -c{n} column URI may hold a transposed-branch marker (axis confusion)"


def test_marker_carried_on_escalation_path(tmp_path):
    """Final-review fix wave (C1, CRITICAL): _emit_unit_markers was called only on the
    seven ASSERTED branches of compile_tables — every escalation branch (and the
    NON_TABLE-ignored branch) silently dropped a band's absorbed marker ink from both
    the graph and the token accounting. currency_marker_escalating_pdf's single band
    absorbs 2 `$` markers but then escalates REGION_TILING_FAILED for an UNRELATED
    reason (a dropped 'Total' header word, not the markers). Post-fix: the ink must
    still land in the graph, attached to the region CANDIDATE uri (cand_uri), never a
    `-c{n}` column fact (no column was ever asserted on an escalated band)."""
    from rdflib import Literal, Namespace, RDF, URIRef
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import currency_marker_escalating_pdf
    TAB = Namespace("https://w3id.org/iladub/tab#")
    pdf = str(tmp_path / "escalating_marker.pdf")
    currency_marker_escalating_pdf(pdf)
    rep = compile_tables(pdf, page_number=0)

    assert len(rep.regions) == 1
    region = rep.regions[0]
    assert region.verdict == "escalated", [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    assert region.reason == "REGION_TILING_FAILED"

    cand_uri = URIRef("https://example.org/etkl/doc#region0")
    markers = list(rep.graph.subjects(RDF.type, TAB.UnitMarker))
    assert len(markers) == 2, "both absorbed $ markers must be carried into the graph"
    for m in markers:
        assert list(rep.graph.objects(m, TAB.markerSymbol)) == [Literal("$")]
        assert list(rep.graph.objects(m, TAB.markerRegion)), "marker without provenance"
        holders = list(rep.graph.subjects(TAB.hasUnitMarker, m))
        assert holders == [cand_uri], \
            f"marker must hang off the region candidate {cand_uri}, not a -c{{n}} column: {holders}"

    # accounting parity: the carried marker words are counted in escalated_total, not
    # silently dropped from the score's denominator.
    assert region.tokens_escalated > 0
    assert rep.escalated > 0 and rep.asserted == 0
